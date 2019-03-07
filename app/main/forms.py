from wtforms.fields import StringField, BooleanField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField
from ..auth.forms import BaseForm


class PostForm(BaseForm):
    title = StringField("标题", validators=[DataRequired()])
    content = PageDownField("内容", validators=[DataRequired()])
    set_private = BooleanField("设为私密")
    article_tag = SelectMultipleField(choices=['A', 'B', 'B', 'D'])
    classify_tag = SelectMultipleField(choices=['Python', 'Java', 'CSAPP'])
    submit = SubmitField("发表文章")







