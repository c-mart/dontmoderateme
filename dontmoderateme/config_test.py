SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/dontmoderateme-test.sqlite'
SECRET_KEY = 'CHANGEME123'
TESTING = True
RATELIMIT_ENABLED = False
WTF_CSRF_ENABLED = False  # "WTF_" prefix apparently required here
MAIL_SUPPRESS_SEND = True