from . import global_view
from flask import request, redirect, url_for
from ..api.result import api_jsonify, ApiResult


@global_view.route('/login_err')
@api_jsonify
def login_err():
    if 'next' in request.args and request.args['next'].startswith('/api'):
        return ApiResult(error='请先登录', message='请先登录')
    else:
        return redirect(url_for('auth.login'))