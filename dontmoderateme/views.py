from dontmoderateme import app, limiter, login_manager, mail
import dontmoderateme.models as models
import dontmoderateme.forms as forms
import dontmoderateme.helpers as helpers
from flask import redirect, url_for, request, session, flash, render_template, make_response, g
import flask_login
import flask_mail
from sqlalchemy.orm.exc import NoResultFound
import base64
from datetime import datetime
import humanize
import os
from jinja2 import Markup


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


def send_password_reset_email(email_addr, token):
    """Sends password reset email including passed token_string to passed email_addr."""
    reset_url = url_for('reset_password', token=token, _external=True)
    body = "Please visit this page to reset your password: %s" % reset_url
    html_body = "Please click this link to reset your password: <a href=\"{0}\">{0}</a>".format(reset_url)
    msg = flask_mail.Message(subject="Reset your password on Don't Moderate Me",
                             sender="notify@dontmoderate.me",
                             recipients=[email_addr],
                             body=body,
                             html=html_body)
    mail.send(msg)


def send_feedback_email(text, sender_email):
    msg = flask_mail.Message(subject="DMM user feedback from " + sender_email,
                             sender="feedback@dontmoderate.me",
                             recipients=[app.config['FEEDBACK_EMAIL']],
                             body=text)
    mail.send(msg)


@login_manager.user_loader
def user_loader(user_id):
    """Retrieves user object associated with user_id for login manager."""
    try:
        return models.User.query.filter_by(id=int(user_id)).one()
    except NoResultFound:
        return None


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/feedback', methods=['GET', 'POST'])
@limiter.limit('2/minute', methods=['POST'])
def feedback():
    """Collect feedback from user and send it"""
    form = forms.FeedbackForm()
    if request.method == 'GET':
        return render_template('feedback.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            send_feedback_email(form.text.data, form.email.data)
            flash("We've got your message! If you provided an email address, we'll get back to you soon.")
            return render_template('feedback.html', form=form)
        else:
            # Form validation failed, tell user to fix their input
            flash("There was a problem with the information you entered, please see below")
            return render_template('feedback.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit('3/minute', methods=['POST'])
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
            # Confirm that email address does not exist already
            if models.User.query.filter_by(email=form.email.data).first():
                flash('There is already an account for that email address.<br /> Please log in or reset your password.')
                return redirect(url_for('login'))
            user = models.User(form.email.data, form.password.data)
            models.db.session.add(user)
            models.db.session.commit()
            send_activation_email(user)
            return render_template('activate.html')
        else:
            # Validation failed, tell user to fix their input
            flash('There was a problem with the information you entered, please see below.')
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
                    flash('No active account with that email and password, try again.')
                    return render_template('login.html', form=form)
        else:
            # Return form to user and tell them to fix their input
            return render_template('login.html', form=form)


@flask_login.login_required
@app.route('/logout')
def logout():
    """Logs user out."""
    flask_login.logout_user()
    flash('You are logged out.')
    return redirect(url_for('home'))


@app.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Generate password reset token and send password reset email to user"""
    form = forms.ResetPasswordRequestForm()
    if flask_login.current_user.is_authenticated is True:
        flash("You're already logged in, log out to request a password reset.")
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('reset_password_request.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = models.User.query.filter_by(email=form.email.data).first()
            if user:
                # Re-use existing token if we have one, else generate new token and store in database
                token_obj = models.PasswordResetToken.query.filter_by(user_id = user.id).first()
                if token_obj:
                    token = token_obj.token
                else:
                    token = base64.urlsafe_b64encode(os.urandom(16)).decode('ascii')
                    token_obj = models.PasswordResetToken(user.id, token)
                    models.db.session.add(token_obj)
                    models.db.session.commit()
                send_password_reset_email(user.email, token)
                flash('Password reset email sent! Please check your inbox or spam folder for a password reset link.')
                return render_template('reset_password_request.html', form=form)
            else:
                flash('No account with that email address. Please try again or register a new account.')
                return render_template('reset_password_request.html', form=form)
        else:
            # Form input validation failed, re-present form with error messages
            return render_template('reset_password_request.html', form=form)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Authenticate password reset request based on token provided and allow user to reset password."""
    if flask_login.current_user.is_authenticated is True:
        flash("You're already logged in, log out to reset your password.")
        return redirect(url_for('home'))
    form = forms.ResetPasswordForm()
    token_obj = models.PasswordResetToken.query.filter_by(token=token).first_or_404()
    user_id = token_obj.user_id
    user = models.User.query.filter_by(id=user_id).first_or_404()
    if request.method == 'GET':
        return render_template('reset_password.html', form=form, token=token)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user.set_password(form.password.data)
            models.db.session.delete(token_obj)
            models.db.session.commit()
            flash("Your password has been reset, please log in with your new password.")
            return redirect(url_for('login'))
        else:
            # Form input validation failed
            return render_template('reset_password.html', form=form, token=token)


@flask_login.login_required
@app.route('/dashboard')
def dashboard():
    """View dashboard"""
    monitors = models.Monitor.query.filter_by(user=flask_login.current_user).\
        order_by(models.Monitor.create_timestamp.desc()).all()
    checks = models.Check.query.filter_by(user=flask_login.current_user, changed=True).\
        order_by(models.Check.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', monitors=monitors, checks=checks)


@flask_login.login_required
@app.route('/view-monitor/<monitor_id>')
def view_monitor(monitor_id):
    """View an existing monitor"""
    monitor = models.Monitor.query.filter_by(id=monitor_id, user=flask_login.current_user).first_or_404()
    checks = models.Check.query.filter_by(monitor=monitor, user=flask_login.current_user)\
        .order_by(models.Check.timestamp.desc()).limit(50).all()
    events = models.Check.query.filter_by(monitor=monitor, user=flask_login.current_user, changed=True)\
        .order_by(models.Check.timestamp.desc()).all()
    return render_template('view_monitor.html', monitor=monitor, events=events, checks=checks)


@flask_login.login_required
@app.route('/create-monitor', methods=['GET', 'POST'])
def create_monitor():
    """Create a new monitor"""
    form = forms.MonitorForm()
    if request.method == 'GET':
        return render_template('create_edit_monitor.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            monitor = models.Monitor(user_id=flask_login.current_user.id,
                                     url=form.url.data,
                                     text=form.text.data,
                                     description=form.description.data)
            models.db.session.add(monitor)
            models.db.session.commit()
            flash('Monitor created successfully.')
            return redirect(url_for('view_monitor', monitor_id=monitor.id))
        else:
            # Validation failed, tell user to fix their input
            flash('There was a problem creating your monitor, please see below.')
            return render_template('create_edit_monitor.html', form=form)


@flask_login.login_required
@app.route('/edit-monitor/<monitor_id>', methods=['GET', 'POST'])
def edit_monitor(monitor_id):
    """Edit existing monitor"""
    monitor = models.Monitor.query.filter_by(id=monitor_id, user=flask_login.current_user).first_or_404()
    form = forms.MonitorForm(request.form, monitor)
    if request.method == 'GET':
        return render_template('create_edit_monitor.html', form=form, monitor=monitor, edit=True)
    elif request.method == 'POST':
        if form.validate_on_submit():
            monitor.url = form.url.data
            monitor.text = form.text.data
            monitor.description = form.description.data
            models.db.session.commit()
            flash('Monitor updated successfully.')
            return redirect(url_for('view_monitor', monitor_id=monitor.id))
        else:
            # Validation failed, tell user to fix their input
            flash('There was a problem updating your monitor, please see below.')
            return render_template('create_edit_monitor.html', form=form, monitor=monitor, edit=True)


@flask_login.login_required
@app.route('/delete-monitor/<monitor_id>')
def delete_monitor(monitor_id):
    """Delete a monitor"""
    monitor = models.Monitor.query.filter_by(id=monitor_id, user=flask_login.current_user).first_or_404()
    models.db.session.delete(monitor)
    models.db.session.commit()
    flash('Monitor has been deleted.')
    return redirect(url_for('dashboard'))


@flask_login.login_required
@app.route('/event-image/<check_id>')
def view_event_image(check_id):
    check = models.Check.query.filter_by(id=check_id, user=flask_login.current_user).first_or_404()
    response = make_response(check.screenshot)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


@app.errorhandler(429)
def rate_limit_exceeded_handler(e):
    """Warns user that they have hit the rate limiter."""
    flash('You have tried doing that too often. Please wait a minute before trying again.')
    return make_response(redirect(request.referrer))

# Jinja2 display filters - perhaps these should go in their own module


@app.template_filter('friendly_state')
def friendly_state(state):
    """Returns human-friendly text for state of monitor"""
    if state is None:
        return Markup("Check again in a minute")
    elif state is False:
        return Markup("<img class=\"icon\" src=\"%s\" /> Down" % url_for('static', filename='icons/down-icon-16px.png'))
    elif state is True:
        return Markup("<img class=\"icon\" src=\"%s\" /> Up" % url_for('static', filename='icons/up-icon-16px.png'))


@app.template_filter('human_elapsed_time')
def human_elapsed_time(timestamp):
    """Returns human-friendly text for time elapsed since timestamp"""
    return humanize.naturaldelta(datetime.utcnow() - timestamp)


@app.template_filter('localized_time')
def localized_time(timestamp):
    """Returns a localized timestamp using moment.js"""
    return Markup("<script>document.write(moment(\"%s\").format('%s'));</script><noscript>%s</noscript>"
                  % (timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                     'LLL',
                     timestamp.strftime('%Y-%m-%d %H:%M') + ' UTC'))
