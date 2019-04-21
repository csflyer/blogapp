# @Time : 2019-03-08 17:01 
# @Author : Crazyliu
# @File : forms.py
from ..auth.forms import BaseForm
from ..models import User
from flask_login import current_user
from wtforms.fields import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, StopValidation


class ProfileForm(BaseForm):
    username = StringField('用户名', validators=[DataRequired()])
    sex = SelectField("性别", choices=[('male', "男"), ("female", "女"), ("0", "性别不详")], validators=[DataRequired()])
    location = StringField('居住地', validators=[DataRequired(), Length(max=50)])
    about_me = TextAreaField('个人简介', validators=[Length(max=200)])
    submit = SubmitField("修改")

    def validate_username(self, field):
        if field.data != current_user.username and \
                User.query.filter_by(username=field.data).first() is not None:
            raise StopValidation("该用户名已有人使用，请更换后再试!")





