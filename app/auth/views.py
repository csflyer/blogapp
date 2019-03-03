from . import auth
from flask import render_template, session, make_response, request, flash, redirect, url_for, get_flashed_messages
from ..tools.verify_code import VerifyImage
from ..tools.send_mail import send_mail
from .forms import LoginForm, RegisterForm
from ..tools.tool import FlashMsg
from datetime import datetime
from ..Status import UserStatus
from .. import db
import json
from flask_login import current_user, login_user, logout_user
from ..models import User


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if current_user.status == UserStatus.Unconfirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirm'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if not login_user(user, form.remember_me.data):
                FlashMsg.error("登录失败， 您的账号" + user.email + "已被封禁！")
            else:
                FlashMsg.info("欢迎回来，" + user.username)
            return redirect(url_for('main.index'))
        else:
            form.password.data = ''
            form.verify_code.data = ''
            return render_template('baseform/form.html', form=form)
    return render_template('baseform/form.html', form=form)


@auth.route('/logout')
def logout():
    FlashMsg.info(current_user.username + "已安全退出登录")
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
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirm_token()
        send_mail(user.email, "激活账户", template="mail/register", user=user, token=token)
        FlashMsg.info("激活邮件已发送到您的邮箱，请先登录再点击邮件中的激活链接！")
        return redirect(url_for('main.index'))
    else:
        form.password = form.password2 = form.verify_code = ''
    return render_template('baseform/form.html', form=form)


@auth.route('/confirm/<token>')
def confirm(token):
    if current_user.status != UserStatus.Unconfirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        FlashMsg.info("您已成功激活账户" + current_user.username + "!")
    else:
        FlashMsg.warning("您的激活链接已过期，请重新申请!")
    return redirect(url_for("main.index"))


@auth.route('/unconfirm')
def unconfirm():
    if current_user.is_anonymous or current_user.is_confirmed:
        return redirect(url_for('main.index'))
    return render_template("auth/unconfirm.html")


@auth.route('/resend_confirmation')
def resend_confirmation():
    if current_user.is_confirmed:
        return redirect(url_for('main.index'))
    token = current_user.generate_confirm_token()
    send_mail(current_user.email, "激活账户", template="mail/register", user=current_user, token=token)
    return redirect(url_for('main.index'))


@auth.route('/change_password')
def change_password():
    pass










