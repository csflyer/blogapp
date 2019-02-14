from . import auth
from flask import render_template
from datetime import datetime
from .. import db
import json
from ..models import Post, User, Role


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')




