from dontmoderateme import app, limiter, login_manager, mail
import dontmoderateme.models as models
import dontmoderateme.forms as forms
import dontmoderateme.helpers as helpers
from flask import redirect, url_for, request, session, flash, render_template, make_response, g
import flask_login
import flask_mail
from sqlalchemy.orm.exc import NoResultFound
import base64

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit('1/minute', methods=['POST'])
def register():
    """Render login page or process login attempt"""
    form = forms.RegistrationForm()
    if request.method == 'GET':
        return render_template('register.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if len(form.password.data) < 8:
                flash('Please use a password with at least 8 characters.')
                return render_template('register.html', form=form)
            # Confirm that email address does not exist already
            if models.User.query.filter_by(email=form.email.data).first():
                flash('There is already an account for that email address.<br /> Please log in or reset your password.')
                return redirect(url_for('login'))
            # Create new user
            user = models.User(form.email.data, form.password.data)
            models.db.session.add(user)
            models.db.session.commit()
            # Send activation email
            activation_url = url_for('activate', id=user.id, code=base64.urlsafe_b64encode(user.pw_hash), _external=True)
            body = "Please visit this link to activate your account: %s" % activation_url
            html_body = "Please activate your account: <a href=\"{0}\">{0}</a>".format(activation_url)
            msg = flask_mail.Message(subject="Activate your account on Don't Moderate Me",
                                     sender="activation@dontmoderate.me",
                                     recipients=[form.email.data],
                                     body=body,
                                     html=html_body)
            mail.send(msg)
            return render_template('activate.html', form=form)

        else:
            # Return form to user and tell them to fix their input
            return render_template('register.html', form=form)


@app.route('/activate', methods=['GET'])
def activate():
    return request.args.get('id') + " and " + request.args.get('code')
    # todo finish this


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
                    if user.activated is True:
                        flask_login.login_user(user)
                        flash('You are logged in.')
                        return redirect(url_for('dashboard'))
                    else:
                        flash('You have not activated your account yet, please follow the link in the activation email.')
                        return render_template('activate.html')
        else:
            # Return form to user and tell them to fix their input
            return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.errorhandler(429)
def rate_limit_exceeded_handler(e):
    """Warns user that they have hit the rate limiter."""
    flash('You have tried doing that too often. Please wait a minute before trying again.')
    return make_response(redirect(request.referrer))