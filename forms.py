# the file contains all the forms used in the web app

# imports flask form to use for forms
from flask_wtf import FlaskForm
# imports required fields
from wtforms import StringField, PasswordField, SubmitField, BooleanField
# imports validators
from wtforms.validators import DataRequired, Length, Email, EqualTo

# the form for users to register
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    consent = BooleanField('I consent to receive emails')
    submit = SubmitField('Sign Up')

# the form for users to query URLs
class URLForm(FlaskForm):
    url =  StringField('Enter URL', validators=[DataRequired(), Length(min=20, max=255)])
    submit = SubmitField('Check URL')

# the form for users to login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
