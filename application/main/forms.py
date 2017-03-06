from flask.ext.pagedown.fields import PageDownField
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class EditProfileForm(Form):
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')


class PostForm(Form):
    title = StringField('标题', validators=[DataRequired()])
    content = PageDownField("文章内容", render_kw={'rows': '30'}, validators=[DataRequired()])
    new_tag = StringField('标签', validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentForm(Form):
    email = StringField('邮箱地址', validators=[DataRequired()])
    content = StringField('评论内容', validators=[DataRequired()])
    submit = SubmitField('提交')
