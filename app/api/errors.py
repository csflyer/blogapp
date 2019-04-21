from . import api
from .result import ApiResult, api_jsonify, NotFoundResult, ServerErrorResult


@api.errorhandler(404)
def not_found(e):
    return NotFoundResult()(), 404


@api.errorhandler(500)
@api_jsonify
def server_internal_error(e):
    return ServerErrorResult()(), 500
