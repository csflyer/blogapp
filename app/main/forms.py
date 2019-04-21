from flask_login import current_user
from .. import db
from ..models import ClassifyTag, User, Post
from wtforms.fields import StringField, BooleanField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, StopValidation
from flask_pagedown.fields import PageDownField
from ..auth.forms import BaseForm


class ClassifyTagField(SelectMultipleField):
    def __init__(self, *args, **kwargs):
        super(ClassifyTagField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        html = super(ClassifyTagField, self).__call__(*args, **kwargs)
        append_html = '<div class="input-group input-group-sm add_tag_list margin_bottom_10">' \
                      '<input id="add_tag_input" type=text class="form-control" aria-label=''Action''>' \
                      '<span class=''input-group-btn''>' \
                      '<button id="add_tag_btn" class="btn btn-primary btn-sm">添加分类</button>' \
                      '</span>' \
                      '</div>'
        return append_html + html

    def validate(self, form, extra_validators=tuple()):
        return True

    def pre_validate(self, form):
        return True


class PostForm(BaseForm):
    title = StringField("标题", validators=[DataRequired(), Length(max=64)])
    summary = StringField("摘要", validators=[DataRequired(), Length(max=170)])
    content = PageDownField("内容", validators=[DataRequired()])
    set_private = BooleanField("设为私密")
    article_tag = StringField("文章标签", validators=[DataRequired()])
    classify_tag = ClassifyTagField()
    submit = SubmitField("发表文章")

    def validate_title(self, field):
        if Post.query.filter_by(title=field.data).first() is not None:
            raise StopValidation('标题重复，请更换再试!')


class ClassifyTagForm(BaseForm):
    tag = StringField('', validators=[DataRequired()])

    # def validate_tag(self, field):
    #     tag_name = field.data
    #     if list(filter(lambda tag: tag.name == tag_name, current_user.classifytags)):
    #         raise StopValidation('已存在该分类!')
    #     else:
    #         classifytag = ClassifyTag(name=tag_name, user=current_user)
    #         db.session.add(classifytag)
    #         db.session.commit()









