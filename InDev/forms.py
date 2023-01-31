from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from InDev.models import Developer
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        developer = Developer.query.filter_by(username=username_to_check.data).first()
        if developer:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = Developer.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exist! Please try a different email address')

    first_name = StringField(label='First Name:', validators=[Length(min=2, max=30), DataRequired()])
    last_name = StringField(label="Last Name:")
    username = StringField(label='Username:')
    email_address = StringField(label="E-mail Address:", validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Creat Account')


class LoginForm(FlaskForm):
    username = StringField(label='Username:', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')


class UpdateDevForm(FlaskForm):
    first_name = StringField(label='First Name:', validators=[Length(min=2, max=30), DataRequired()])
    last_name = StringField(label="Last Name:")
    username = StringField(label='Username:')
    update = SubmitField(label="Update")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content")
    submit = SubmitField("Submit")


class EditPostForm(FlaskForm):
    content = CKEditorField("Content")
    submit = SubmitField("Update")


class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")
