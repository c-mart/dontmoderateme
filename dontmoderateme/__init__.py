from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_login
import flask_limiter
import flask_mail

app = Flask(__name__)
app.config.from_object('dontmoderateme.config_default')
db = SQLAlchemy(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
limiter = flask_limiter.Limiter()
limiter.init_app(app)
mail = flask_mail.Mail(app)

import dontmoderateme.views

if __name__ == '__main__':
    app.run()