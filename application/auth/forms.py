from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError

from application.models import User


class LoginForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              '用户名中只能有字母，'
                                              '数字，英文句号和下划线')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码必须匹配')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('此邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('已经有人使用的用户名')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧的密码', validators=[DataRequired()])
    password = PasswordField('新的密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码必须匹配')
    ])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('更新密码')


class PasswordResetRequestForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码必须匹配')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('未知的邮箱地址')


class ChangeEmailForm(Form):
    email = StringField('新的邮箱', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('更新邮箱地址')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('已经注册过的邮件地址')
