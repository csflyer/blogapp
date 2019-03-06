import time, uuid
from datetime import datetime
from .Status import TokenString
from . import login_manager
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .Status import UserStatus
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


class Follow(db.Model):
    __tablename__ = 'follows'

    # 记录关注者的id, 关注的id 和 关注的时间
    follower_id = db.Column(db.String(50), db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.String(50), db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    __tablename__ = 'users'

    # 基本信息
    id = db.Column(db.String(50), primary_key=True, default=next_id)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(32), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    sex = db.Column(db.String(6))
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
        return self.generate_token(expiration, TokenString.Confirm, self.id)

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

    def generate_reset_password_token(self, expiration):
        return self.generate_token(expiration, TokenString.ResetPassword, self.id)

    @staticmethod
    def generate_token(key_or_dict, value=None, expiration=None):
            s = Serializer(current_app.config['SECRET_KEY'],
                           expires_in=expiration or current_app.config['EMAIL_EXPIRATION'])
            return s.dumps({key_or_dict: value} if isinstance(key_or_dict, str) else key_or_dict).decode('ascii')

    @staticmethod
    def load_token(self, token, key=None, compare=False, value=None):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        return (data.get(key) == value if compare else data.get(key)) if key else data

    def generate_change_email_token(self, new_email):
        data = {TokenString.ChangeEmail: self.id, TokenString.NewEmail: new_email}
        return self.generate_token(data)

    def confirm_change_email_token(self, token):
        if not token:
            return False
        data = self.load_token(token)
        if not data or data.get(TokenString.ChangeEmail) or data.get(TokenString.NewEmail):
            return False
        if self.id != data.get(TokenString.ChangeEmail):
            return False
        self.email = data.get(TokenString.NewEmail)
        db.session.add(self)
        db.session.commit()
        return True



    @staticmethod
    def reset_password(self, token, new_password):
        user_id = self.load_token(token, TokenString.ResetPassword)
        if user_id:
            user = User.get_or_404(user_id)
            user.password = new_password
            db.session.add(user)
            return True
        return False




    def __repr__(self):
        return '<User name:%r>' % self.username


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

    def __repr__(self):
        return '<Role name:%r>' % self.name


class ClassifyTag(db.Model):
    '''
    博客文章的分类标签
    '''
    ___tablename__ = 'classifytags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    # 关联信息
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'))


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
    content_html = db.Column(db.Text)
    view_nums = db.Column(db.Integer, index=True, default=0)
    status = db.Column(db.String(8))
    create_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_at = db.Column(db.DateTime, index=True)

    # 关联信息
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    articletags = db.relationship('ArticleTag', backref='post', lazy='dynamic')
    classifytags = db.relationship('ClassifyTag', secondary=ClassifyTagRegistration,
                                   backref=db.backref('posts', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<Role title:%r>' % self.title


class Comment(db.Model):
    '''
    博客的评论类
    '''
    __tablename__ = 'comments'

    id = db.Column(db.String(50), primary_key=True, default=next_id)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    floor = db.Column(db.Integer)
    ref_id = db.Column(db.String(50), index=True, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(8))

    # 关联信息
    author_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    post_id = db.Column(db.String(50), db.ForeignKey("posts.id"))

    def __repr__(self):
        return '<Comment id:%r>' % self.id


class ArticleTag(db.Model):
    '''
    博客文章的文章标签
    '''
    __tablename__ = 'articletags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    # 关联信息
    post_id = db.Column(db.String(50), db.ForeignKey('posts.id'))


# class ExternalUser(db.Model):
#     '''
#     博客的外部用户类 如微博 QQ等
#     '''
#     pass
