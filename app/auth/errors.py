from . import auth
from flask import render_template, current_app
from ..tools.tool import Log


@auth.errorhandler(404)
def page_not_found(e):
    Log.warning(e)
    return render_template("baseform/404.html")


@auth.errorhandler(500)
def internal_server_error(e):
    Log.error(e)
    return render_template("baseform/500.html")
