from flask import session
from ..models import User, UserStatus
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo


class EmailForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('邮箱或密码错误!')


class PasswordForm(FlaskForm):
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 20)])

    def validate_password(self, field):
        if field.data.isalnum() or field.data.isalpha():
            raise ValidationError('密码必须同时包含字母和数字')


class UsernameForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 16)])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('此昵称已有人使用，请更换您的昵称')


class RememberMeForm(FlaskForm):
    remember_me = BooleanField()


class VerifyCodeForm(FlaskForm):
    verify_code = StringField('验证码', validators=[DataRequired(), Length(min=4, max=4)])

    def validate_verify_code(self, field):
        if field.data.upper() != session['verify_code'].upper():
            raise ValidationError('验证码错误!')


class SubmitForm(FlaskForm):
    def __call__(self, name):
        class SubSumitForm:
            submit = SubmitField(name)
        return SubSumitForm


class BasicForm(EmailForm, PasswordField, VerifyCodeForm):
    def validate_email(self, field):
        pass


class BasicAuthForm(EmailForm, PasswordForm, VerifyCodeForm):
    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is None or not user.verify_password(self.password.data):
            raise ValidationError('邮箱或密码错误!')
        if user.status == UserStatus.Forbidden:
            raise ValidationError('账号已封禁，请联系管理员!')

    def validate_password(self, field):
        pass


class LoginForm(BasicAuthForm, RememberMeForm, SubmitForm('登陆')):
    pass


class RegisterForm(BasicForm, SubmitForm('注册')):
    password2 = PasswordField('重复密码', validators=[DataRequired(), EqualTo('password')])


















