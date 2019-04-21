import re
from . import api
from .. import db
from ..models import User, Post, ClassifyTag
from flask import request, current_app, url_for
from .result import ApiResult, BadRequestResult, api_jsonify
from flask_login import login_required, current_user

email_re = re.compile(r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$')


@api.route('/users/<id>')
@login_required
@api_jsonify
def get_user(id):
    '''
        用于首页获取用户信息
    :param id:
    :return:
    '''
    if hasattr(current_user, 'id') and current_user.id == id:
        user = current_user
    else:
        user = User.query.get_or_404(id)
    return ApiResult(**user.to_dict())


@api.route('/users/<id>/posts/')
@login_required
@api_jsonify
def get_user_posts(id):
    '''
    获取用户中心获取自己的写的文章
    :param id:
    :return:
    '''
    if hasattr(current_user, 'id') and current_user.id == id:
        user = current_user
    else:
        user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    order_by = request.args.get('order', 'time', type=str)
    if order_by == 'hottest':
        pagination = user.posts.order_by(Post.view_nums.desc()).pagination(
            page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
    else:
        pagination = user.posts.order_by(Post.created_at.desc()).pagination(
            page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
    posts = pagination.items
    prev = next = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page-1, _external=True)
    if pagination.has_next:
        next = url_for('api.get_user_posts', id=id, page=page+1, _external=True)
    return ApiResult(
        posts=[post.to_dict() for post in posts],
        prev=prev,
        next=next,
        count=pagination.total,
    )


@api.route('/users/timeline/')
@api_jsonify
def get_user_followed_posts():
    '''
        用于首页用户的时间线上的文章 显示所有文章 无需登陆
    :param id:
    :return:
    '''
    user = current_user
    page = request.args.get('page', 1, type=int)
    order_by = request.args.get('order', 'time', type=str)
    if order_by == 'hottest':
        pagination = user.followed_posts.order_by(Post.view_nums.desc()).pagination(
            page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
    else:
        pagination = user.followed_posts.order_by(Post.created_at.desc()).pagination(
            page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
    posts = pagination.items
    prev = next = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_posts', id=id, page=page-1, _external=True)
    if pagination.has_next:
        next = url_for('api.get_user_followed_posts', id=id, page=page+1, _external=True)
    return ApiResult(
        posts=[post.to_dict() for post in posts],
        prev=prev,
        next=next,
        count=pagination.total
    )


@api.route('/users/register', methods=['POST'])
@api_jsonify
def register():
    '''
        用户注册Api
    :return:
    '''
    data = request.json
    email = data.get('email')
    password = data.get('password')
    confirm = data.get('confirm')
    username = data.get('username')
    if not (email and password and confirm and username):
        return ApiResult(error='402', message='字段不能为空!')
    if not email_re.match(email):
        return ApiResult(error='402', message='邮箱格式错误!')
    if password != confirm:
        return ApiResult(error='402', message='两次密码不一致!')
    if password.isnumeric() or password.isalpha():
        return ApiResult(error='402', message='密码不能全为数字或字母!')
    if len(password) < 6:
        return ApiResult(error='402', message='密码长度过短!')
    if len(password) > 20:
        return ApiResult(error='402', message='密码长度过长!')
    refuse_list = ['123456', 'abc', 'abcde']
    for item in refuse_list:
        if item in password:
            return ApiResult(error='402', message='密码过于简单!')
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return ApiResult(error='402', message='已有人使用该昵称!请更改昵称再试!')
    user = User(email=email, password=password, username=username)
    db.session.add(user)
    db.session.commit()
    return ApiResult()


@api.route('/add-tag', methods=['POST'])
@api_jsonify
def add_tag():
    tag_name = request.form.get('tag')
    if isinstance(tag_name, str):
        if list(filter(lambda tag: tag.name == tag_name, current_user.classifytags)):
            return BadRequestResult(message='已存在该分类标签')
        else:
            classifytag = ClassifyTag(name=tag_name, user=current_user)
            db.session.add(classifytag)
            db.session.commit()
            return ApiResult()
    else:
        return BadRequestResult()





















