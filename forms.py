from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email
from wtforms import ValidationError
from models import User
from database import db


class RegisterForm(FlaskForm):
    class Meta:
        csrf = False

    firstname = StringField('First Name', validators=[Length(1, 20),
        Regexp('[a-zA-Z]+', message='First name cannot include spaces, numbers, or special characters'),
    ])

    lastname = StringField('Last Name', validators=[Length(1, 20),
        Regexp('[a-zA-Z]+', message='Last name cannot include spaces, numbers, or special characters')
    ])

    email = StringField('Email', [
        Email(message='Not a valid email address.'),
        DataRequired()])

    password = PasswordField('Password', validators=[
        DataRequired(message="Please enter a password."),
        EqualTo('confirmPassword', message='Passwords must match'),
        Length(min=6, max=16),
        Regexp('(?=.*[A-Z])(?=.*[a-z])(?=(.*[0-9]){2,})(?=(.*[!@#$%^&*_=+?<>,.`~:;]){2,})', 
            message='Password must have both upper and lowercase letters, two numbers, and two special characters')
    ])

    confirmPassword = PasswordField('Confirm Password', validators=[
        Length(min=6, max=16)
    ])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() != 0:
            raise ValidationError('Email already in use.')


class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    email = StringField('Email', [
        Email(message='Not a valid email address.'),
        DataRequired()])

    password = PasswordField('Password', [
        DataRequired(message="Please enter a password.")])

    submit = SubmitField('Submit')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() == 0:
            raise ValidationError('Incorrect email or password.')

class CommentForm(FlaskForm):
    class Meta:
        csrf = False

    comment = TextAreaField('Add a Comment', validators=[Length(min=0, max=300)])

    submit = SubmitField('Add Comment')