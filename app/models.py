import hashlib
from random import randint
import time, uuid
from math import ceil
from datetime import datetime
from .Status import TokenString, Permission
from . import login_manager
from flask import current_app, url_for, abort
from flask_login import current_user
from markdown import markdown
import bleach
from flask_login import AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .Status import UserStatus
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from sqlalchemy import and_
from sqlalchemy.sql import func


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser


class Follow(db.Model):
    __tablename__ = 'follows'

    # 记录关注者的id, 关注的id 和 关注的时间
    follower_id = db.Column(db.String(50), db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.String(50), db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def fake_follow():
        users = User.query.all()
        for i in range(50):
            first_index = randint(0, len(users)-1)
            second_index = randint(0, len(users)-1)
            if first_index == second_index:
                continue
            else:
                follow = Follow(follower_id=users[first_index].id, \
                                followed_id=users[second_index].id)
                db.session.add(follow)
        db.session.commit()



class Role(db.Model):
    '''
    博客的登录角色类
    '''
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    permission = db.Column(db.Integer, default=0)

    # 关联信息
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        for attr in dir(Permission):
            if '_' not in attr and not attr.isupper():
                role = Role(name=attr, permission=getattr(Permission, attr))
                db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role name:%r>' % self.name


class User(db.Model):
    __tablename__ = 'users'

    # 基本信息
    id = db.Column(db.String(50), primary_key=True, default=next_id)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(32), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    sex = db.Column(db.String(6))
    location = db.Column(db.String(64))
    user_image = db.Column(db.String(128))
    about_me = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime)

    # 其他状态信息
    status = db.Column(db.String(16), index=True, default=UserStatus.Unconfirmed)

    # 关联信息
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    classifytags = db.relationship('ClassifyTag', backref='user', lazy='dynamic')
    posts = db.relationship('Post', backref='user', lazy='dynamic')

    followed = db.relationship('Follow',
                                foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        # 默认角色为user
        self.role_id = 3
        super(User, self).__init__(*args, **kwargs)
        if self.email is not None and not self.user_image:
            self.user_image = hashlib.md5(self.email.decode('utf-8')).hexdigest()

    def gravatar(self, size=40, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.user_image or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.user_id) \
            .filter(Follow.follower_id == self.id)

    # region password dealing
    @property
    def password(self):
        raise ValueError('Password is not a readable property!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    # endregion

    # region login methods related to Flask-Login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return not self.is_forbidden

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
    # endregion

    # region register and confirm
    def generate_confirm_token(self, expiration=3600):
        return self.generate_token(TokenString.Confirm, value=self.id, expiration=expiration)

    def confirm(self, token):
        if not token:
            return False
        if self.load_token(token, TokenString.Confirm, compare=True, value=self.id):
            self.status = UserStatus.Normal
            db.session.add(self)
            db.session.commit()
            return True
        return False
    # endregion

    def generate_auth_token(self, expiration=3600):
        return self.generate_token(TokenString.Auth, value=self.id, expiration=expiration)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def can(self, permission):
        return self.role.permission == Permission.ADMINISTRATER or permission & self.role.permission == permission

    @property
    def is_confirmed(self):
        return self.status != UserStatus.Unconfirmed

    @is_confirmed.setter
    def is_confirmed(self):
        raise ValueError('is_confirmed is not a writable attribute!')

    @property
    def is_forbidden(self):
        return self.status == UserStatus.Forbidden

    @is_forbidden.setter
    def is_forbidden(self):
        raise ValueError('is_forbidden is not a writable attribute!')

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def to_dict(self):
        return {
            'id' : self.id,
            'username': self.username,
            'sex': self.sex,
            'email': self.email,
            'role': self.role.name,
            'member_since': self.created_at,
            'last_seen': self.last_seen,
            'posts': '',
            'status': getattr(UserStatus, self.status)
        }

    def generate_reset_password_token(self, expiration=3600):
        return self.generate_token(TokenString.ResetPassword, self.id, expiration)

    def confirm_reset_password_token(self, token):
        if not token:
            return False
        data = self.load_token(token)
        if not data \
                or not data.get(TokenString.ResetPassword):
            return False
        return data.get(TokenString.ResetPassword)

    @staticmethod
    def generate_token(key_or_dict, value=None, expiration=None):
            s = Serializer(current_app.config['SECRET_KEY'],
                           expires_in=expiration or current_app.config['EMAIL_EXPIRATION'])
            return s.dumps({key_or_dict: value} if isinstance(key_or_dict, str) else key_or_dict).decode('ascii')

    @staticmethod
    def load_token(token, key=None, compare=False, value=None):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        return (data.get(key) == value if compare else data.get(key)) if key else data

    def generate_change_email_token(self, new_email):
        data = {TokenString.ChangeEmail: self.id, TokenString.NewEmail: new_email}
        return self.generate_token(data, expiration=3600)

    def confirm_change_email_token(self, token):
        if not token:
            return False
        data = self.load_token(token)
        if not data or not data.get(TokenString.ChangeEmail) or not data.get(TokenString.NewEmail):
            return False
        if self.id != data.get(TokenString.ChangeEmail):
            return False
        self.email = data.get(TokenString.NewEmail)
        db.session.add(self)
        db.session.commit()
        return True

    @staticmethod
    def reset_password(token, email, new_password):
        user_id = User.load_token(token, TokenString.ResetPassword)
        user = User.query.filter_by(email=email).first()
        if user_id and user_id == user.id:
            user.password = new_password
            db.session.add(user)
            db.session.commit()
            return True
        return False

    @staticmethod
    def generate_fake():
        import forgery_py
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        from datetime import datetime
        seed()
        print('begin to insert', datetime.now())
        for i in range(50):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     status=UserStatus.Normal,
                     sex=['Male', 'Female', ''][randint(0, 2)],
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     created_at=forgery_py.date.date(True),
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        print('insert end', datetime.now())


    @staticmethod
    def add_self_follow():
        users = User.query.all()
        for user in users:
            follow = Follow(followed_id=user.id, follower_id=user.id)
            db.session.add(follow)
        db.session.commit()

    @property
    def followed_id_list(self):
        return list(map(lambda user: user.id, self.followed.all()))

    @property
    def followers_id_list(self):
        return list(map(lambda user: user.id, self.followers.all()))

    def __repr__(self):
        return '<User name:%r>' % self.username


class ClassifyTag(db.Model):
    '''
    博客文章的分类标签
    '''
    ___tablename__ = 'classifytags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    # 关联信息
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'))

    @staticmethod
    def query_by_name(str_or_list):
        if isinstance(str_or_list, list):
            return ClassifyTag.qeury.filter(ClassifyTag.name.in_(str_or_list)).all()
        else:
            return ClassifyTag.query.filter_by(name=str_or_list).first()

    @staticmethod
    def generate_fake():
        import forgery_py
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        from datetime import datetime
        seed()

        users = User.query.all()
        print('begin to insert', datetime.now())
        for i in range(50):
            tag = ClassifyTag(name=forgery_py.lorem_ipsum.word(),
                            user=users[randint(0, len(users) - 1)])
            db.session.add(tag)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        print('insert end', datetime.now())

    @classmethod
    def find_most_tag(cls):
        if current_user.is_anonymous:
            sql = 'select b.name, b.total from' \
                  ' (select ct.name, count(post_id) as total from classifytagregistration a join classify_tag ct on a.tag_id = ct.id' \
                  '     group by ct.name) b' \
                  ' order by b.total desc limit 6'
        else:
            sql = 'select b.name, b.total from ' \
                  '(select ct.name, count(post_id) as total from classifytagregistration a join classify_tag ct on a.tag_id = ct.id' \
                  '     where ct.user_id = \'{}\'' \
                  '     group by ct.name) b' \
                  ' order by b.total desc limit 6'.format(current_user.id)
        return db.session.execute(sql).fetchall()


    def __repr__(self):
        return '<ClassifyTag name:%r>' % self.name


ClassifyTagRegistration = db.Table('classifytagregistration',
                                   db.Column('post_id', db.String(50), db.ForeignKey('posts.id')),
                                   db.Column('tag_id', db.Integer, db.ForeignKey(ClassifyTag.id)))


class Post(db.Model):
    '''
    博客的文章类
    '''
    __tablename__ = 'posts'

    id = db.Column(db.String(50), primary_key=True, default=next_id)
    title = db.Column(db.String(64), unique=True)
    type = db.Column(db.String(8))
    content = db.Column(db.Text)
    summary = db.Column(db.String(170))
    content_html = db.Column(db.Text)
    view_nums = db.Column(db.Integer, index=True, default=0)
    status = db.Column(db.String(8))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, index=True)

    # 关联信息
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    articletags = db.relationship('ArticleTag', backref='post', lazy='dynamic')
    classifytags = db.relationship('ClassifyTag', secondary=ClassifyTagRegistration,
                                   backref=db.backref('posts', lazy='dynamic'), lazy='dynamic')

    @staticmethod
    def on_change_content(target, value, oldvalue, initiator):
        target.content_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=current_app.config['POST_ALLOW_TAGS'],
            strip=True))

    def to_dict(self):
        attrs = ['id', 'title', 'type', 'content', 'summary', 'view_nums','status', 'created_at', 'updated_at']
        result = {}
        for k in attrs:
            result[k] = getattr(self, k)
        comment_pages = ceil(self.comments.filter_by(reply_id=None).count() / \
                             current_app.config['COMMENTS_PER_PAGE'])
        result['comment_pages'] = comment_pages
        return result

    def ping(self):
        self.view_nums = self.view_nums + 1
        db.session.add(self)
        db.session.commit()

    @property
    def first_level_comments(self):
        return self.comments.filter(Comment.reply_id==None).all()

    @staticmethod
    def generate_fake():
        import forgery_py
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        from datetime import datetime
        seed()

        users = User.query.all()
        print('begin to insert', datetime.now())
        for i in range(50):
            print(forgery_py.date.date(True))
            u = Post(title=forgery_py.lorem_ipsum.word(),
                     content=forgery_py.lorem_ipsum.sentences(as_list=False),
                     summary=forgery_py.lorem_ipsum.sentence(),
                     view_nums=randint(0, 1000),
                     user=users[randint(0, len(users) - 1)]
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        print('insert end', datetime.now())


    @staticmethod
    def generate_summary(body):
        '''
            生成summary
        :param body: post markdown格式正文
        :return: TODO:
        '''
        return ''

    @staticmethod
    def from_json(json):
        '''
            从request.json新建一个post
        :param self:
        :param json:
        :return:
        '''
        title = json.get('title')
        content = json.get('content')
        summary = json.get('summary')
        private = json.get('set_private')
        post = Post(title=title, content=content, summary=summary, type='private' if private else 'public')
        return post

    def update_from_json(self, json):
        '''
            从request.json更新post
        :return:
        '''
        title = json.get('title')
        content = json.get('content')
        classify_tags = json.get('classify_tags')
        article_tags = json.get('article_tags')
        self.title = title or self.title
        self.content = content or self.content
        if self.body == content:
            self.summary = Post.generate_summary(self.content)


    def update_from_form(self, form):
        self.title = form.title.data or self.title
        self.summary = form.summary.data or self.summary
        self.content = form.content.data or self.content
        self.type = 'private' if form.set_private.data else 'public'
        self.user = current_user
        article_tag = form.article_tag.data
        article_tag = (article_tag[:-1] if article_tag[-1] == ';' else article_tag).split(';')
        user_article_tag = self.articletags.all()
        user_article_tag_name_list = list(map(lambda x: x.name, user_article_tag))
        for tag in filter(lambda x: x.name not in article_tag, user_article_tag):
            self.articletags.remove(tag)
        for tag in filter(lambda x: x not in user_article_tag_name_list, article_tag):
            new_tag = ArticleTag(name=tag, post_id=self.id)
            db.session.add(new_tag)

        classify_tags = form.classify_tag.data
        post_classify_tag = self.classifytags.all()
        post_classify_tag_name_list = list(map(lambda tag: tag.name, post_classify_tag))
        for tag in filter(lambda tag: tag.name not in classify_tags, post_classify_tag):
            self.classifytags.remove(tag)
        to_append_tag_list = list(filter(lambda tag: tag not in post_classify_tag_name_list, classify_tags))
        if to_append_tag_list:
            tags = ClassifyTag.query.filter(and_(ClassifyTag.name.in_(to_append_tag_list), ClassifyTag.user_id==current_user.id)).all()
            for tag in tags:
                self.classifytags.append(tag)
        db.session.add(self)
        db.session.commit()


    def __repr__(self):
        return '<Post title:%r>' % self.title


class Comment(db.Model):
    '''
    博客的评论类
    '''
    __tablename__ = 'comments'

    id = db.Column(db.String(50), primary_key=True, default=next_id)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    floor = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(8))
    reply_id = db.Column(db.String(50), db.ForeignKey('comments.id'))
    replies = db.relationship('Comment', back_populates='comment')
    comment = db.relationship('Comment', back_populates='replies', remote_side=[id])

    # 关联信息
    author_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    post_id = db.Column(db.String(50), db.ForeignKey("posts.id"))

    def to_dict(self):
        '''
            嵌套评论
        :return:
        '''
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at,
            'username': self.user.username,
            'user_image': self.user.user_image,
            'replies': [reply.to_dict() for reply in self.replies]
        }

    @staticmethod
    def from_json(json):
        return Comment(
            content=json.get('content') or abort(404)
        )

    @staticmethod
    def generate_fake():
        import forgery_py
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        from datetime import datetime
        seed()

        posts = Post.query.all()
        comments=[]
        print('begin to insert', datetime.now())
        for i in range(50):
            post = posts[randint(0, len(posts) - 1)]
            print(post, randint(0, len(comments) - 1) if i else None)
            comment = comments[randint(0, len(comments) - 1)] if i > 0 else None
            u = Comment(content=forgery_py.lorem_ipsum.sentence(),
                        post=post,
                        user=post.user,
                        comment=comment if randint(0, 10) > 5 else None
                     )
            comments.append(u)
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        print('insert end', datetime.now())

    def __repr__(self):
        return '<Comment id:%r>' % self.id


class ArticleTag(db.Model):
    '''
    博客文章的文章标签
    '''
    __tablename__ = 'articletags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    # 关联信息
    post_id = db.Column(db.String(50), db.ForeignKey('posts.id'))

    @staticmethod
    def query_by_name(str_or_list):
        if isinstance(str_or_list, list):
            return ArticleTag.qeury.filter(ArticleTag.name.in_(str_or_list)).all()
        else:
            return ArticleTag.query.filter_by(name=str_or_list).first()

    @staticmethod
    def generate_fake():
        import forgery_py
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        from datetime import datetime
        seed()

        posts = Post.query.all()
        print('begin to insert', datetime.now())
        for i in range(50):
            post = posts[randint(0, len(posts) - 1)]
            u = ArticleTag(name=forgery_py.lorem_ipsum.word(),
                        post=post,
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        print('insert end', datetime.now())

    def __repr__(self):
        return '<ArticleTag name:%r>' % self.name


# class ExternalUser(db.Model):
#     '''
#     博客的外部用户类 如微博 QQ等
#     '''
#     pass

db.event.listen(Post.content, 'set', Post.on_change_content)
