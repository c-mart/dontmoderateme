from datetime import timedelta

"""
These are example configuration values. Change them to something different for use in production.
"""

SERVER_NAME = '127.0.0.1:5000'

SQLALCHEMY_DATABASE_URI = 'postgresql://dmm-dev:changeme123@localhost/dmm-dev'
SECRET_KEY = 'CHANGEME123'
RATELIMIT_ENABLED = True

RECAPTCHA_PUBLIC_KEY = '6LdwgxoTAAAAAPY1e613368XN8jzZDB6p81JQgX-'
RECAPTCHA_PRIVATE_KEY = '6LdwgxoTAAAAAAhWGmubwN-vN5sGfzncJEU3Ol9O'
RECAPTCHA_DATA_ATTRS = {'theme': 'dark'}

MAIL_SERVER = 'smtp.west.cox.net'

SPLASH_ENDPOINT = 'http://localhost:8050'  # Splash container
MONITOR_CHECK_INTERVAL = timedelta(minutes=10)  # timedelta object specifying how often each monitor should be checked
DAEMON_WAKEUP_INTERVAL = 60  # Time in seconds specifying how often check_daemon should wake up and perform checks
CHECK_DAEMON_LOG_FILE = '/tmp/check_daemon'

FEEDBACK_EMAIL = 'test@example.com'

USER_MAX_MONITORS = 60  # Limit each user to this many monitors