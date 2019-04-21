from flask import Blueprint
from .result import ApiResult

api = Blueprint('api', __name__)


from . import errors, post, user, authentication


@api.after_request
def after_request(response):
    headers = response.headers
    headers['Access-Control-Allow-Origin'] = 'http://localhost:8000'
    headers['Access-Control-Allow-Methods'] = 'GET,POST'
    headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    headers['Access-Control-Allow-Credentials'] = 'true'
    return response
