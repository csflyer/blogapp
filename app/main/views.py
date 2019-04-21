from . import main
from .. import db
from ..tools.tool import Log
from random import randint
from ..Status import Permission
from ..models import Post, ArticleTag, ClassifyTag, Comment
from flask_login import current_user, login_required
from flask import render_template, request,current_app, redirect, url_for, jsonify, abort, session
from .forms import PostForm, ClassifyTagForm


@main.before_request
def before_request():
    if isinstance(session['verify_code'], int):
        session['verify_code'] = randint(0, 1000)

@main.route('/')
def index():
    order_by = request.args.get('order_by', 'time')
    page = request.args.get('page', 1, type=int)
    target_posts = Post.query if current_user.is_anonymous else current_user.followed_posts
    if order_by == 'hottest':
        pagination = target_posts.order_by(Post.view_nums.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
    else:
        pagination = target_posts.order_by(Post.created_at.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
    posts = pagination.items
    tags = ClassifyTag.find_most_tag()
    return render_template('main/index.html', posts=posts, pagination=pagination, order_by=order_by, tags=tags)


@main.route('/classifytag/<name>')
@login_required
def classifytag(name):
    tag = current_user.classifytags.filter_by(name=name).first()
    page = request.args.get('page', 1, type=int)
    pagination = tag.posts.order_by(Post.created_at.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    tags = ClassifyTag.find_most_tag()
    return render_template('main/index.html', posts=posts, pagination=pagination, tags=tags, now_tag=tag)


@main.route('/search')
def search():
    pass


@main.route('/posts/<id>')
def post(id):
    post = Post.query.get_or_404(id)
    post.ping()
    return render_template('main/post.html', post=post)


@main.route('/new_post', methods=['GET', 'POST'])
@login_required
@Permission.Required(Permission.WRITE_ARTICLES)
def new_post():
    Log.info('Try to Write New Post')
    form = PostForm()
    tag_list = list(map(lambda x: (x.name, x.name), current_user.classifytags))
    form.classify_tag.choices = tag_list
    if form.validate_on_submit():
        post = Post.from_json(request.form)
        post.user = current_user
        article_tag = form.article_tag.data
        article_tag = article_tag[:-1] if article_tag[-1] == ';' else article_tag
        db.session.add_all(list(map(lambda x: ArticleTag(name=x.strip(), post=post), article_tag.split(';'))))
        tag_list = ClassifyTag.query.filter(ClassifyTag.name.in_(form.classify_tag.data)).all()
        post.classifytags = tag_list
        db.session.add(post)
        db.session.commit()
        Log.info('New Post Success: {}'.format(post.id))
        return redirect(url_for('main.post', id=post.id))
    return render_template("main/new_post.html", form=form)


@main.route('/posts/<id>/edit', methods=['GET', 'POST'])
@login_required
@Permission.Required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    Log.info('Try to Edit Post: {}'.format(post.id))
    if post.user.id != current_user.id and not current_user.can(Permission.ADMINISTRATER):
        abort(501)
    form = PostForm()
    tag_list = list(map(lambda x: (x.name, x.name), current_user.classifytags))
    form.classify_tag.choices = tag_list
    if request.method == 'POST':
        post.update_from_form(form)
        return redirect(url_for('main.post', id=post.id))
    form = PostForm(obj=post)
    form.classify_tag.choices = tag_list
    form.article_tag.data = ';'.join(list(map(lambda tag: tag.name, post.articletags)))
    return render_template("main/new_post.html", form=form)


@main.route('/posts/<id>/add_comment', methods=['POST'])
@login_required
@Permission.Required(Permission.COMMENT)
def new_comment(id):
    post = Post.query.get_or_404(id)
    Log.info('Try to Write Comment to Post: {}'.format(post.id))
    content = request.form.get('content')
    ref_id = request.form.get('ref_id')
    if not content:
        return jsonify({
            'error': '400',
            'message': '评论内容不能为空!',
            'data': ''
        })
    if len(content) > 500:
        return jsonify({
            'error': '400',
            'message': '评论内容过长!',
            'data': ''
        })
    comment = Comment.query.get(ref_id) if ref_id else None
    if ref_id and (not comment):
        return jsonify({
            'error': '400',
            'message': '错误的请求!',
            'data': ''
        })
    new_comment = Comment(content=content)
    new_comment.post_id = post.id
    new_comment.user = current_user
    if comment:
        comment.replies.append(new_comment)
    db.session.add(new_comment)
    db.session.commit()
    Log.info('Add New Comment Success: {}'.format(comment.id))
    return jsonify({
            'error': '',
            'message': '',
            'data': ''
        })


@main.route('/add-tag', methods=['POST'])
@login_required
@Permission.Required(Permission.WRITE_ARTICLES)
def add_tag():
    tag_name = request.form.get('tag')
    Log.info('Try to add New Tag: {}'.format(tag_name))
    if isinstance(tag_name, str) and tag_name and  len(tag_name) < 64:
        if list(filter(lambda tag: tag.name == tag_name, current_user.classifytags)):
            return jsonify({
                'error': '400',
                'message': '已存在该分类标签',
                'data': ''
            })
        else:
            classifytag = ClassifyTag(name=tag_name, user=current_user)
            db.session.add(classifytag)
            db.session.commit()
            return jsonify({
                'error': '',
                'message': '',
                'data': ''
            })
    else:
        return jsonify({
            'error': '400',
            'message': '标签名字不能为空,且要少于64个字符',
            'data': ''
        })
