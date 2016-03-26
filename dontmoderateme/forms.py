from flask_wtf import Form, RecaptchaField
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, URL, Email, EqualTo, Length


class LoginForm(Form):
    """Log in an existing user"""
    email = StringField('Email Address',
                        default=None,
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             default=None,
                             validators=[DataRequired()])


class RegistrationForm(Form):
    """Register a new user"""
    email = StringField('Email Address',
                        default=None,
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             default=None,
                             validators=[DataRequired(),
                                         Length(min=8)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[EqualTo('password',
                                                         message='Passwords must match')])
    recaptcha = RecaptchaField()


class MonitorForm(Form):
    """Create or update a monitor"""
    url = StringField('Which URL should we check?',
                      validators=[DataRequired(),
                                  URL()])
    text = TextAreaField('What text should we look for?', validators=[DataRequired()])
    description = StringField('Brief description (optional)')
    recaptcha = RecaptchaField('Are you a robot?')