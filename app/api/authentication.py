from . import api
from ..models import User
from flask import request
from flask_login import current_user, login_user, logout_user
from .result import ApiResult, api_jsonify, BadRequestResult, AuthFailResult


@api.route('/user/login', methods=['POST', 'OPTION'])
@api_jsonify
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    remember_me = data.get('remember_me')
    if not (email and password):
        return BadRequestResult()
    user = User.query.filter_by(email=email).first()
    if user is None:
        return BadRequestResult()
    if not user.verify_password(password):
        return AuthFailResult()
    login_user(user, remember_me)
    return ApiResult(message='ok', id=user.id, permission=user.role.permission)


@api.route('/user/logout')
@api_jsonify
def logout():
    # if current_user.is_anonymous:
    #     return BadRequestResult()
    logout_user()
    return ApiResult(message='ok')

