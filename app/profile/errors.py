from . import profile
from flask import render_template


@profile.errorhandler(404)
def page_not_found():
    return render_template("baseform/404.html")


@profile.errorhandler(500)
def internal_server_error():
    return render_template("baseform/500.html")
