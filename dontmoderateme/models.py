from dontmoderateme import db, helpers
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

    def __init__(self, email, password, enabled=True, activated=False):
        self.email = email
        self.pw_salt = urandom(16)
        self.pw_hash = helpers.pw_hash(password, self.pw_salt)
        self.enabled = enabled
        self.activated = activated
        self.create_date = datetime.utcnow()

    def __repr__(self):
        return '<User %s>', self.email

    @property
    def is_authenticated(self):
        """Flask-login requires this for some reason"""
        return True

    @property
    def is_active(self):
        """Returns boolean indicating whether user is active (i.e. they can log in)."""
        return self.active

    @property
    def is_anonymous(self):
        """Flask-login requires this for some reason"""
        return False

    def get_id(self):
        """Flask-login requires this for some reason"""
        return self.id


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
        return self.checks


class Check(db.Model):
    """Check object. Belongs to a monitor, indicates the results of a page load and result of match."""

    id = db.Column(db.Integer, primary_key=True)
    monitor_id = db.Column(db.Integer, db.ForeignKey('monitor.id'))
    monitor = db.relationship('Monitor', backref=db.backref('checks', lazy='dynamic'))
    result = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)
    changed = db.Column(db.Boolean)
    screenshot = None  # todo figure this out

    def __init__(self, monitor_id, result, timestamp=None, screenshot=None):
        self.monitor_id = monitor_id
        self.result = result
        self.timestamp = timestamp or datetime.utcnow()
        # If the previous check returned a different result than this check, set changed to True
        prev_check = Check.query.order_by(Check.timestamp.desc()).first()
        if prev_check is not None:
            prev_result = prev_check.result
            if prev_result != result:
                self.changed = True
            else:
                self.changed = False
        # Todo retrieve and store screenshot (or reference to it) if changed is True

    def __repr__(self):
        return '<Check ' + str(self.result) + ' on ' + self.monitor.url + '>'
