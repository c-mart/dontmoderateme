from dontmoderateme import db, helpers
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from os import urandom


class User(db.Model):
    """User object"""

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    pw_hash = db.Column(db.Binary)
    pw_salt = db.Column(db.Binary)
    activated = db.Column(db.Boolean)  # Set to True once user clicks link in activation email
    enabled = db.Column(db.Boolean)
    create_timestamp = db.Column(db.DateTime)

    def set_password(self, password):
        self.pw_hash = helpers.pw_hash(password, self.pw_salt)

    def __init__(self, email, password, enabled=True, activated=False):
        self.email = email
        self.pw_salt = urandom(16)
        self.set_password(password)
        self.enabled = enabled
        self.activated = activated
        self.create_timestamp = datetime.utcnow()

    def __repr__(self):
        return '<User %s>', self.email

    @property
    def is_authenticated(self):
        """Flask-login requires this for some reason"""
        return True

    @property
    def is_active(self):
        """Returns boolean indicating whether user is enabled (i.e. they can log in)."""
        return self.enabled

    @property
    def is_anonymous(self):
        """Flask-login requires this for some reason"""
        return False

    def get_id(self):
        """Flask-login requires this for some reason"""
        return self.id


class PasswordResetToken(db.Model):
    """Stores tokens used to authenticate users for a password reset."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('reset_tokens', lazy='dynamic'))
    token = db.Column(db.String)

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

    def __repr__(self):
        return "<Password reset token for user ID %s>" % self.user_id


class Monitor(db.Model):
    """Monitor object. Belongs to a user, knows a URL and a string of text to look for at that URL"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('monitors', lazy='dynamic'))
    url = db.Column(db.String)
    text = db.Column(db.Text)
    description = db.Column(db.String)
    create_timestamp = db.Column(db.DateTime)

    def __init__(self, user_id, url, text, create_timestamp=None, description=None):
        self.url = url
        self.text = text
        self.user_id = user_id
        self.create_timestamp = create_timestamp or datetime.utcnow()
        self.description = description

    def __repr__(self):
        return '<Monitor for %s>' % self.url

    @property
    def state(self):
        last_check = self.checks.order_by(Check.timestamp.desc()).first()
        if last_check is not None:
            return last_check.result
        return None

    @hybrid_property
    def last_check_time(self):
        """Returns last check time of a monitor as a datetime object.
        Returns Unix Epoch if monitor has never been checked."""
        last_check = Check.query.filter_by(monitor_id=self.id).order_by(Check.timestamp.desc()).first()
        if last_check is None:
            return datetime.utcfromtimestamp(0)
        return last_check.timestamp





class Check(db.Model):
    """Check object. Belongs to a monitor, indicates the results of a page load and result of match."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('checks', lazy='dynamic'))
    monitor_id = db.Column(db.Integer, db.ForeignKey('monitor.id'))
    monitor = db.relationship('Monitor', backref=db.backref('checks', lazy='dynamic'))
    result = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)
    changed = db.Column(db.Boolean)
    screenshot = db.Column(db.LargeBinary)

    def __init__(self, monitor_id, result, screenshot=None, timestamp=None):
        self.monitor_id = monitor_id
        self.user_id = Monitor.query.filter_by(id=monitor_id).one().user_id
        self.result = result
        self.timestamp = timestamp or datetime.utcnow()
        # This check is changed (and screenshot is stored) if there is no previous check or if result has changed
        prev_check = Check.query.filter_by(monitor_id=self.monitor_id).order_by(Check.timestamp.desc()).first()
        # TODO refactor this block to DRY
        if prev_check is not None:
            if prev_check.result == result:
                self.changed = False
            else:
                self.changed = True
                self.screenshot = screenshot
        else:
            self.changed = True
            self.screenshot = screenshot

    def __repr__(self):
        return '<Check ' + str(self.result) + ' for monitor ID ' + str(self.monitor_id) + ' on ' + str(self.timestamp) + '>'