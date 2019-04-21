from . import api
from .. import db
from ..models import Post, User
from flask_login import  current_user
from flask_login import login_required
from flask import request, current_app, url_for
from .result import ApiResult, api_jsonify, BadRequestResult, PermissionFailResult


@api.route('/posts/')
@login_required
@api_jsonify
def get_posts():
    '''用于首页展现的所有posts'''
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.pagination(
        page, per_page=current_app.config['POSTS_PER_PAGE'],err_out=False
    )
    posts = pagination.items
    prev = next = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return ApiResult(
        post=[post.to_dict() for post in posts],
        prev=prev,
        next=next,
        count=pagination.total
    )


@api.route('/posts/<id>')
@api_jsonify
def get_post(id):
    '''
        用于点击文章显示具体的文章内容
    :param id:
    :return:
    '''
    post = Post.query.get_or_404(id)
    return ApiResult(post=post.to_dict())


# TODO: 待添加权限
@api.route('/posts', methods=['POST'])
@api_jsonify
def new_post():
    '''
    创建新文章的APi
    :return:
    '''
    try:
        post = Post.from_json(request.json)
    except ValueError as e:
        return BadRequestResult(message=str(e.args[0]))
    post.author = current_user._get_current_object()
    db.session.add(post)
    db.session.commit()
    return ApiResult(Location=url_for('api.get_post', id=post.id, _external=True))


# TODO: 待添加权限
@api.route('/posts/<id>', methods=['PUT'])
@api_jsonify
def edit_post(id):
    '''
    编辑文章APi
    :param id:
    :return:
    '''
    post = Post.query.get_or_404(id)
    if current_user != post.user:
        return PermissionFailResult()
    post = post.update_json(request.json)
    db.session.add(post)



