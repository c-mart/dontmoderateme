"""
These are example configuration values. Change them to something different for use in production.
"""

SERVER_NAME = '127.0.0.1:5000'

SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/dontmoderateme.sqlite'
SECRET_KEY = 'CHANGEME123'
RATELIMIT_ENABLED = True

RECAPTCHA_PUBLIC_KEY = '6LdwgxoTAAAAAPY1e613368XN8jzZDB6p81JQgX-'
RECAPTCHA_PRIVATE_KEY = '6LdwgxoTAAAAAAhWGmubwN-vN5sGfzncJEU3Ol9O'
RECAPTCHA_DATA_ATTRS = {'theme': 'dark'}

MAIL_SERVER = 'smtp.west.cox.net'