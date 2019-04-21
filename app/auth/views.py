from . import auth
from random import randint
from flask_login import login_required
from flask import render_template, session, make_response, request, redirect, url_for
from ..tools.verify_code import VerifyImage
from ..tools.send_mail import send_mail
from ..tools.tool import Log
from .forms import LoginForm, RegisterForm, ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm, ChangeEmailForm
from ..tools.tool import FlashMsg
from ..Status import UserStatus
from .. import db
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
    if isinstance(session['verify_code'], int):
        session['verify_code'] = randint(0, 1000)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            Log.info('Try to Login : {}'.format(user.email))
            if not login_user(user, form.remember_me.data):
                FlashMsg.error("登录失败， 您的账号" + user.email + "已被封禁！")
                Log.warning('Login Failure : {}'.format(user.email))
            else:
                FlashMsg.info("欢迎回来，" + user.username)
                Log.info('Login Success:{}'.format(user.email))
            return redirect(url_for('main.index'))
        else:
            form.password.data = ''
            form.verify_code.data = ''
            return render_template('baseform/form.html', form=form)
    return render_template('baseform/form.html', form=form)


@auth.route('/logout')
def logout():
    FlashMsg.info(current_user.username + "已安全退出登录")
    Log.info('Login Out Success:{}')
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
        Log.info('Try to Register:{}'.format(user.email))
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirm_token()
        Log.info('Try to Send Register Email:{}'.format(user.email))
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
    Log.info('Try to Confirm:{}'.format(current_user.email))
    if current_user.confirm(token):
        Log.info('Confirm Success:{}'.format(current_user.email))
        FlashMsg.info("您已成功激活账户" + current_user.username + "!")
    else:
        Log.info('Confirm Failure:{}'.format(current_user.email))
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
    Log.info('Try to Resend Confirm Email:{}')
    token = current_user.generate_confirm_token()
    send_mail(current_user.email, "激活账户", template="mail/register", user=current_user, token=token)
    FlashMsg.info("激活邮件已发送到您的邮箱,如未找到，请确认邮件是否被系统归类在垃圾箱中!")
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    Log.info('Try to Change Password:{}')
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        Log.info('Change Password Success:{}')
        FlashMsg.info('已成功修改密码,请使用新密码登录!')
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('baseform/form.html',form=form)


# 用户不需要登录 先输入邮箱和验证码后 点击邮箱中的链接再输入新的密码即可
@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        Log.info('Try to Reset Password:{}')
        token = user.generate_reset_password_token()
        Log.info('Try to Send Reset Password Email:{}')
        send_mail(form.email.data, "重设您的密码", "mail/reset_password", token=token, user=user)
        FlashMsg.info('已向您的邮箱发送重设密码链接，请注意查收!')
        return redirect(url_for('main.index'))
    return render_template('baseform/form.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        result = User.reset_password(token, form.email.data, form.password.data)
        if result:
            Log.info('Reset Password Success:{}'.format(result))
            FlashMsg.info('重置密码成功!请用新的密码登录!')
            return redirect('auth.login')
        else:
            FlashMsg.error('重置密码失败!')
            Log.warning('Reset Password Failure:{}'.format(result))
    return render_template('baseform/form.html', form=form)


# 用户在登录模式下 输入新的邮箱地址, 然后点击邮箱链接即可
@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        Log.info('Try to Change Email:{}')
        token = current_user.generate_change_email_token(form.email.data)
        Log.info('Try to Send Change Email')
        send_mail(form.email.data, "重设您的密码", "mail/change_email", token=token, user=current_user)
        FlashMsg.info('重设邮件已发往新的邮件地址，请注意查收!')
        return redirect(url_for('main.index'))
    return render_template('baseform/form.html', form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if not current_user.confirm_change_email_token(token):
        Log.info('Change Email Failure: Invalid Token')
        FlashMsg.error('非法的Token!')
        return redirect(url_for('main.index'))
    Log.info('Change Email Success')
    logout_user()
    FlashMsg.info('更改邮箱地址成功, 请用新的邮箱地址登录!')
    return redirect(url_for('auth.login'))










