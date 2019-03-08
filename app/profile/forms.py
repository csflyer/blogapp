# @Time : 2019-03-08 17:01 
# @Author : Crazyliu
# @File : forms.py
from ..auth.forms import BaseForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired


class ProfileForm(BaseForm):
    username = StringField('用户名', validators=[DataRequired()])
    submit = SubmitField("修改")




