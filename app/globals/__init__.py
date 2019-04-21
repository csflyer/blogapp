from flask import Blueprint

global_view = Blueprint('global', __name__)

from . import views