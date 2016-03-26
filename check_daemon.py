from dontmoderateme import db, models
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import base64

splash_endpoint = 'http://localhost:8050'  # Splash container
check_interval = timedelta(seconds=60)  # timedelta object specifying how often each monitor should be checked


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

while True:
    stale_time = datetime.utcnow() - check_interval  # Time at which we consider a monitor to be stale
    stale_monitors = models.Monitor.query.filter(models.Monitor.last_check_time < stale_time).all()
    for monitor in stale_monitors:
        new_check = models.Check(monitor, *check(monitor.url, monitor.text))
        db.session.add(new_check)
        db.session.commit()
    time.sleep(60)