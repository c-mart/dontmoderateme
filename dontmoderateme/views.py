from dontmoderateme import app, limiter, login_manager, mail
import dontmoderateme.models as models
import dontmoderateme.forms as forms
import dontmoderateme.helpers as helpers
from flask import redirect, url_for, request, session, flash, render_template, make_response, g
import flask_login
import flask_mail
from sqlalchemy.orm.exc import NoResultFound
import base64


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


@flask_login.login_required
@app.route('/logout')
def logout():
    """Logs user out."""
    flask_login.logout_user()
    flash('You are logged out.')
    return redirect(url_for('home'))


@flask_login.login_required
@app.route('/dashboard')
def dashboard():
    """View dashboard"""
    monitors = models.Monitor.query.filter_by(user=flask_login.current_user).\
        order_by(models.Monitor.create_timestamp.desc()).all()
    checks = models.Check.query.filter_by(user=flask_login.current_user, changed=True).\
        order_by(models.Check.timestamp.desc()).all()
    return render_template('dashboard.html', monitors=monitors, checks=checks)


@flask_login.login_required
@app.route('/view-monitor/<monitor_id>')
def view_monitor(monitor_id):
    """View an existing monitor"""
    monitor = models.Monitor.query.filter_by(id=monitor_id, user=flask_login.current_user).first_or_404()
    return render_template('view_monitor.html', monitor=monitor)


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


@app.errorhandler(429)
def rate_limit_exceeded_handler(e):
    """Warns user that they have hit the rate limiter."""
    flash('You have tried doing that too often. Please wait a minute before trying again.')
    return make_response(redirect(request.referrer))

# Jinja2 display filters


@app.template_filter('friendly_state')
def friendly_state(state):
    """Returns human-friendly text for state of monitor"""
    if state is None:
        return "Check again soon"
    elif state is False:
        return "Monitor is down!"
    elif state is True:
        return "Monitor is up"
