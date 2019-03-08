# @Time : 2019-03-08 12:34 
# @Author : Crazyliu
# @File : __init__.py
from flask import Blueprint

profile = Blueprint('profile', __name__)

from . import errors, views
