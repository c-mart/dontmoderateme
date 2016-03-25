from dontmoderateme import app, limiter, login_manager
import flask_login
import dontmoderateme.models as models
import dontmoderateme.forms as forms
import dontmoderateme.helpers as helpers
from flask import redirect, url_for, request, session, flash, render_template, make_response, g
from sqlalchemy.orm.exc import NoResultFound

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit('6/minute', methods=['POST'])
def login():
    """Render login page or process login attempt"""
    form = forms.LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            try:
                user = models.User.query.filter_by(email=form.email.data).one()
            except NoResultFound:
                flash('No active account with that email and password, try again.')
                return render_template('login.html', form=form)
            else:
                if user.pw_hash == helpers.pw_hash(form.password.data, user.pw_salt):
                    flask_login.login_user(user)
                    flash('You are logged in.')
                    return redirect(url_for('dashboard'))
        else:
            # Return form to user and tell them to fix their shit
            return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.errorhandler(429)
def rate_limit_exceeded_handler(e):
    """Warns user that they have hit the rate limiter."""
    flash('You have tried doing that too often. Please wait a minute before trying again.')
    # Return statement should be generalized if we ever use rate limiting for actions other than logging in
    return make_response(redirect(url_for('login')))