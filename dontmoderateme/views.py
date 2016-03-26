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
def home():
    return render_template('index.html')

@login_manager.user_loader
def user_loader(user_id):
    """Retrieves user object for login manager."""
    try:
        return models.User.query.filter_by(id=int(user_id)).one()
    except NoResultFound:
        return None

def send_activation_email(user):
    """Sends account activation email to passed user object"""
    activation_url = url_for('activate', code=base64.urlsafe_b64encode(user.pw_salt), _external=True)
    body = "Please visit this page to activate your account: %s" % activation_url
    html_body = "Please click this link to activate your account: <a href=\"{0}\">{0}</a>".format(activation_url)
    msg = flask_mail.Message(subject="Activate your account on Don't Moderate Me",
                             sender="activation@dontmoderate.me",
                             recipients=[user.email],
                             body=body,
                             html=html_body)
    mail.send(msg)


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit('1/minute', methods=['POST'])
def register():
    """Render login page or process login attempt"""
    form = forms.RegistrationForm()
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated is True:
            flash("You're already logged in, log out to register for an account")
            return redirect(url_for('home'))
        else:
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
            send_activation_email(user)
            return render_template('activate.html')

        else:
            # Return form to user and tell them to fix their input
            return render_template('register.html', form=form)


@app.route('/activate', methods=['GET'])
def activate():
    """Activate user account from link in activation email."""
    salt = base64.urlsafe_b64decode(request.args.get('code'))
    user = models.User.query.filter_by(pw_salt=salt).first_or_404()
    if user.activated is False:
        user.activated = True
        models.db.session.commit()
        flash("Thanks, your account has been activated! Please log in to continue.")
    else:
        flash("You have already activated your account.")
    return redirect(url_for('login'))


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

@app.route('/logout')
@flask_login.login_required
def logout():
    """Logs user out."""
    flask_login.logout_user()
    flash('You are logged out.')
    return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.errorhandler(429)
def rate_limit_exceeded_handler(e):
    """Warns user that they have hit the rate limiter."""
    flash('You have tried doing that too often. Please wait a minute before trying again.')
    return make_response(redirect(request.referrer))