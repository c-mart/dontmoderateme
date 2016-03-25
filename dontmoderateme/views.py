from dontmoderateme import app, limiter, login_manager
import dontmoderateme.models as models
import dontmoderateme.forms as forms
from flask import redirect, url_for, request, session, flash, render_template, make_response, g

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/login', methods=['GET', '[POST]'])
@limiter.limit('6/minute', methods=['POST'])
def login():
    """Render login page or process login attempt"""
    if request.methods == 'GET':
        return render_template('login.html')

@app.route('/monitors')
def manage_monitors():

    return render_template('manage_monitors.html')