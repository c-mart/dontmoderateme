from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, URL, Email


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
    pass


class MonitorForm(Form):
    """Create or update a monitor"""
    pass
