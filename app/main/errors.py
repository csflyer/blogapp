from . import main
from ..api.result import ApiResult
from flask import request, render_template


@main.app_errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/api'):
        return ApiResult(error=404, message='错误的API请求!')()
    return render_template("baseform/404.html")


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.path.startswith('/api'):
        return ApiResult(error=500, message='服务器发生错误!')()
    return render_template("baseform/500.html")


@main.app_errorhandler(501)
def server_error(e):
    if request.path.startswith('/api'):
        return ApiResult(error=501, message='无权限!')()
    return render_template("baseform/501.html")

