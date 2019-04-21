from flask import session
from flask_login import current_user
from ..models import User
from random import randint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, StopValidation


class BaseForm(FlaskForm):
    class Meta:
        locals = ['zh-CN']

    def __iter__(self):
        token = self.csrf_token
        yield token

        field_names = {token.name}
        for cls in self.__class__.__bases__:
            for field in cls():
                field_name = field.name
                if field_name not in field_names:
                    field_names.add(field_name)
                    yield self[field_name]

        for field_name in self._fields:
            if field_name not in field_names:
                yield self[field_name]


class EmailForm(BaseForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise StopValidation('邮箱或密码错误!')


class Username(BaseForm):
    username = StringField('用户名', validators=[DataRequired(), Length(6, 20)])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() is not None:
            raise StopValidation('该用户名已有人使用，请更换后再试！')


class PasswordForm(BaseForm):
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 20)])

    def validate_password(self, field):
        if field.data.isnumeric() or field.data.isalpha():
            raise StopValidation('密码必须同时包含字母和数字')


class RepeatPasswordForm(BaseForm):
    repeat_password = PasswordField('重复密码', validators=[DataRequired(), EqualTo('password')])


class UsernameForm(BaseForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 16)])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() is not None:
            raise StopValidation('此昵称已有人使用，请更换您的昵称')


class RememberForm(BaseForm):
    remember_me = BooleanField()


class VerifyCodeField(StringField):
    def __call__(self, *args, **kwargs):
        html = super(VerifyCodeField, self).__call__(*args, **kwargs)
        addition = '<span id="code-change" class="input-group-addon">' \
                   '<img id="validate_img" src="/auth/validate_code">' \
                   '</span>'
        return html + addition


class VerifyCodeForm(BaseForm):
    verify_code = VerifyCodeField('验证码', validators=[DataRequired(), Length(min=4, max=4)])

    def validate_verify_code(self, field):
        if field.data.upper() != str(session['verify_code']).upper():
            session['verify_code'] = randint(0, 1000)
            raise StopValidation('验证码错误!')
        session['verify_code'] = randint(0, 1000)


class SubmitForm:
    def __call__(self, name):
        class SubSubmitForm(BaseForm):
            submit = SubmitField(name)
        return SubSubmitForm


class BasicForm(EmailForm, PasswordForm, VerifyCodeForm):
    def validate_email(self, field):
        pass


class BasicAuthForm(BasicForm):
    def validate_email(self, field):
        if len(self.errors) > 0:
            return
        user = User.query.filter_by(email=field.data).first()
        if user is None or not user.verify_password(self.password.data):
            raise StopValidation('邮箱或密码错误!')

    def validate_password(self, field):
        pass


class LoginForm(BasicAuthForm, RememberForm, SubmitForm()('登陆')):
    title = '登录 Crazyliu Blog'
    form_title = '登录 Crazyliu Blog'




class RegisterForm(EmailForm,
                   UsernameForm,
                   PasswordForm,
                   RepeatPasswordForm,
                   VerifyCodeForm,
                   SubmitForm()('注册')):
    title = '注册 Crazyliu Blog'
    form_title = '注册 Crazyliu Blog'

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise StopValidation("您的邮箱已注册, 请直接登录或者找回密码!")


class SubChangePasswordForm(BaseForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired()])
    repeat_password = PasswordField('重复新密码', validators=[DataRequired(), EqualTo('new_password')])

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise StopValidation('密码错误!')

    def validate_new_password(self, field):
        if field.data.isnumeric() or field.data.isalpha():
            raise StopValidation('密码必须同时包含字母和数字')


class ChangePasswordForm(SubChangePasswordForm, VerifyCodeForm, SubmitForm()('修改密码')):
    form_title = title = '修改密码'


class ResetPasswordRequestForm(EmailForm, VerifyCodeForm, SubmitForm()('发送邮件到邮箱')):
    form_title = title = '重设密码'

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise StopValidation('该邮箱还没有进行过注册!')


class ResetPasswordForm(EmailForm, PasswordForm, RepeatPasswordForm, SubmitForm()('重设密码')):
    form_title = title = '重设密码'

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise StopValidation('邮箱地址有误!')


class ChangeEmailForm(EmailForm, VerifyCodeForm, SubmitForm()('更改邮件地址')):
    form_title = title = '重设邮件地址'

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise StopValidation('该邮件地址已注册，请换个地址再试!')



