from . import auth
from flask import render_template, session, make_response, request, flash, redirect, url_for, get_flashed_messages
from ..tools.verify_code import VerifyImage
from .forms import LoginForm
from ..tools.tool import get_form_error_message
from datetime import datetime
from .. import db
import json
from flask_login import login_user, logout_user
from ..models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            login_user(user, form.remember_me.data)
            flash('登陆成功!', category='info')
            return redirect(url_for('main.index'))
        else:
            error_message = get_form_error_message(form)
            flash(error_message)
            form.password.data = ''
            form.verify_code.data = ''
            return render_template('auth/login.html', form=form)
    return render_template('auth/login.html', form=form)


@auth.route('/validate_code')
def validate_code():
    image = VerifyImage()
    session['verify_code'] = image.code
    response = make_response(image.save())
    response.headers['Content-Type'] = 'image/bmp'
    return response


@auth.route('/login_validate_code')
def validate_code():
    image = VerifyImage()
    session['login_verify_code'] = image.code
    response = make_response(image.save())
    response.headers['Content-Type'] = 'image/bmp'
    return response




@auth.route('/register', methods=['GET', 'POST'])
def register():







