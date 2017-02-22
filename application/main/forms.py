from flask.ext.pagedown.fields import PageDownField
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Regexp, ValidationError


class EditProfileForm(Form):
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')


# class EditProfileAdminForm(Form):
#     email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
#     username = StringField('Username', validators=[
#         DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
#                                               'Usernames must have only letters, '
#                                               'numbers, dots or underscores')])
#     confirmed = BooleanField('Confirmed')
#     role = SelectField('Role', coerce=int)
#     name = StringField('Real name', validators=[Length(0, 64)])
#     location = StringField('Location', validators=[Length(0, 64)])
#     about_me = TextAreaField('About me')
#     submit = SubmitField('Submit')
#
#     def __init__(self, user, *args, **kwargs):
#         super(EditProfileAdminForm, self).__init__(*args, **kwargs)
#         self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
#         self.user = user
#
#     def validate_email(self, field):
#         if field.data != self.user.email and \
#                 User.query.filter_by(email=field.data).first():
#             raise ValidationError('Email already registered.')
#
#     def validate_username(self, field):
#         if field.data != self.user.username and \
#                 User.query.filter_by(username=field.data).first():
#             raise ValidationError('Username already in use.')


class PostForm(Form):
    title = StringField('标题', validators=[DataRequired()])
    content = PageDownField("文章内容", validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentForm(Form):
    email = StringField('邮箱地址')
    content = StringField('评论内容', validators=[DataRequired()])
    submit = SubmitField('提交')
