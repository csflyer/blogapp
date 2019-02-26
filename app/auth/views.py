from . import auth
from flask import render_template, session, make_response, request, flash, redirect, url_for, get_flashed_messages
from ..tools.verify_code import VerifyImage
from .forms import LoginForm, RegisterForm
from ..tools.tool import get_form_error_message
from datetime import datetime
from .. import db
import json
from flask_login import current_user, login_user, logout_user
from ..models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            login_user(user, form.remember_me.data)
            flash("欢迎回来，" +user.username, category='info')
            return redirect(url_for('main.index'))
        else:
            form.password.data = ''
            form.verify_code.data = ''
            return render_template('baseform/form.html', form=form)
    return render_template('baseform/form.html', form=form)


@auth.route('/logout')
def logout():
    flash(current_user.username + "已安全退出登录", category='info')
    logout_user()
    return redirect(url_for("main.index"))


@auth.route('/validate_code')
def validate_code():
    image = VerifyImage()
    session['verify_code'] = image.code
    response = make_response(image.save())
    response.headers['Content-Type'] = 'image/bmp'
    return response


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('baseform/form.html', form=form)






