from flask import jsonify
from functools import wraps


class ApiResult(dict):
    def __init__(self, **kwargs):
        new_kwargs = {
            'error': kwargs.get('error') or getattr(self, 'error', None) or '',
            'message': kwargs.get('message') or getattr(self, 'message', None) or '',
            'data': kwargs.get('data') or {}
        }
        if not new_kwargs['data']:
            for k in kwargs.keys():
                if k not in ['error','message']:
                    new_kwargs['data'][k] = kwargs[k]
        super(ApiResult, self).__init__(new_kwargs)

    def __call__(self, *args, **kwargs):
        return jsonify(self)


class PermissionFailResult(ApiResult):
    error = '100'
    message = '您没有该权限!'


class BadRequestResult(ApiResult):
    error = '400'
    message = '非法的请求!'


class AuthFailResult(ApiResult):
    error = '401'
    message = '登录失败!'


class NotFoundResult(ApiResult):
    error = '404'
    message = '请求错误!'


class ServerErrorResult(ApiResult):
    error = '500'
    message = '服务器发生错误!'


def api_jsonify(func):
    @wraps(func)
    def test(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, ApiResult):
            return result()
        if result.__class__.__name__ == 'Response':
            return result
        return jsonify(result)
    return test
