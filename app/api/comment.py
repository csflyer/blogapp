import re
from . import api
from .. import db
from ..models import User, Post, Comment
from flask import request, current_app, url_for
from .result import ApiResult, BadRequestResult, api_jsonify
from flask_login import login_required, current_user


@api.route('/comments/')
@api_jsonify
def get_comments():
    page = request.args.get('page', 1, tyCpe=int)
    pagination = Comment.query.order_by(Comment.created_at.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'], err_out=False
    )
    comments = pagination.items
    prev = next = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)
    return ApiResult(
        comments=[comment.to_dict() for comment in comments],
        prev=prev,
        next=next,
        count=pagination.total
    )


@api.route('/comments/<id>')
@api_jsonify
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return ApiResult(comment.to_dict())


@api.route('/posts/<id>/comments/')
@api_jsonify
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.query.filter_by(reply_id=None).order_by(Comment.created_at.asc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'], err_out=False
    )
    comments = pagination.items
    prev = next = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)
    return ApiResult(
        comments=[comment.to_dict() for comment in comments],
        prev=prev,
        next=next,
        count=pagination.total
    )


@api.route('/posts/<id>/comments', methods=['POST'])
@login_required
@api_jsonify
def new_post_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.user = current_user
    comment.post = post
    if 'reply_to' in request.json:
        reply_to = Comment.query.get_or_404(request.json['reply_to'])
        reply_to.replies.append(comment)
    db.session.add(comment)
    db.session.commit()
    return ApiResult()



