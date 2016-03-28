from flask import Flask, current_app, url_for
from dontmoderateme import app, db, models, mail
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import base64
import flask_mail
from sqlalchemy.orm import joinedload

"""
check_daemon runs in the background. It periodically queries for monitors that are stale (due to be checked) according to configured check_interval. For each stale monitor, a check is performed by making an API call to a Splash instance. HTML and a JPEG image are requested for each check. Text is extracted from HTML and searched for text specified in the monitor. If this returns a match then check returns True, else False.

From the results of each check, a new Check object is created. The Check model handles logic of whether the current check differs from the last one. If it differs then the image is stored in the database, and the user is sent a notification email indicating that their monitor is up/down. If it does not differ then then the image is not stored in the database.
"""

splash_endpoint = 'http://localhost:8050'  # Splash container
check_interval = timedelta(seconds=60)  # timedelta object specifying how often each monitor should be checked
daemon_wakeup_interval = 60  # Time in seconds specifying how often check_daemon should wake up and perform checks

def get_text_from_html(html):
    """Extract and return text from HTML"""
    soup = BeautifulSoup(html, 'html5lib')
    text = soup.get_text()
    return text


def get_page(url):
    """Get text and JPEG image of the web page at URL. Returns a tuple of text and binary image"""
    params = {'url': url, 'html': 1, 'jpeg': 1, 'render_all': 1, 'wait': 1}
    r = requests.get(splash_endpoint + "/render.json", params=params)
    resp_dict = r.json()
    html = resp_dict.get('html')
    image = base64.b64decode(resp_dict.get('jpeg'))
    text = get_text_from_html(html)
    return text, image


def _strip_text(text):
    """Strips whitespace from a string and converts to lower-case for comparison with another string.
    """
    return re.sub("\s*", "", text.lower())


def check(url, search_text):
    """Checks if search_text displays on url, returns tuple of boolean and base64-encoded JPEG image of page"""
    page_text, page_image = get_page(url)
    return _strip_text(search_text) in _strip_text(page_text), page_image


def send_notification_email(check_id):
    """Sends user a notification email based on results of check object corresponding to passed check_id"""
    notify_check = models.Check.query.options(joinedload('user')).filter_by(id=check_id).one()
    with app.app_context():
        monitor_url = url_for('view_monitor', monitor_id=notify_check.monitor.id, _external=True)
        body = "See details and image of monitored web page at {0}".format(monitor_url)
        html_body = "See details and image of monitored web page <a href=\"{0}\">here</a>.".format(monitor_url)
        msg = flask_mail.Message(subject="Monitor {0} for page {1}".format("Up" if notify_check.result is True else "Down",
                                                                           notify_check.monitor.description),
                                 sender="notify@dontmoderate.me",
                                 recipients=[notify_check.user.email],
                                 body=body,
                                 html=html_body)
        mail.send(msg)

while True:
    stale_time = datetime.utcnow() - check_interval  # Time at which we consider a monitor to be stale
    stale_monitors = models.Monitor.query.filter(models.Monitor.last_check_time < stale_time).all()
    db.session.expunge_all()
    for monitor in stale_monitors:
        new_check = models.Check(monitor.id, *check(monitor.url, monitor.text))
        changed = new_check.changed
        db.session.add(new_check)
        db.session.commit()
        if changed is True:
            send_notification_email(new_check.id)
    time.sleep(daemon_wakeup_interval)