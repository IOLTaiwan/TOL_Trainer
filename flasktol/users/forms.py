from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flasktol.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username 帳號', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email 電子郵件', validators=[DataRequired(), Email()])
    password = PasswordField('Password 密碼', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password 確認密碼', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField("Sign up 註冊")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken 該名稱已被使用')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use 該電子郵件已被使用')


class LoginForm(FlaskForm):
    email = StringField('Email 電子郵件', validators=[DataRequired(), Email()])
    password = PasswordField('Password 密碼', validators=[DataRequired()])
    remember = BooleanField("Remember Me 記住帳號")

    submit = SubmitField("Login 登入")


class UpdateAccountForm(FlaskForm):
    username = StringField('Username 帳號', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email 電子郵件', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture 更新帳號相片', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update account 更新帳號")
    access = SelectField("Access Level 權限", validators=[DataRequired()], choices=[('1', "Guest 一般"), ('2', "Trainee 國手"), ('3', "Admin 管理員")])

    def validate_username(self, username):
        if username.data != current_user.username and not current_user.is_admin():
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken 該名稱已被使用')

    def validate_email(self, email):
        if email.data != current_user.email and not current_user.is_admin():
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already in use 該電子郵件已被使用')

    def validate_access(self, access):
        if int(access.data) > 3 or int(access.data) < 1:
            raise ValidationError('Invalid access level 錯誤權限')


class RequestResetForm(FlaskForm):
    email = StringField('Email 電子郵件', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset 要求密碼重置')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email 此電子郵件沒有註冊帳戶')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password 密碼', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password 確認密碼', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password 重置密碼')
