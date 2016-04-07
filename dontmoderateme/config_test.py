# SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/dontmoderateme-test.sqlite'
SQLALCHEMY_DATABASE_URI = 'postgresql://dmm-test:changeme123@localhost:5433/dmm-test'
SECRET_KEY = 'CHANGEME123'
TESTING = True
RATELIMIT_ENABLED = False
WTF_CSRF_ENABLED = False  # "WTF_" prefix apparently required here
MAIL_SUPPRESS_SEND = True
