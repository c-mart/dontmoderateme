import requests
import re
from bs4 import BeautifulSoup

splash_endpoint = 'http://localhost:8050'


def get_text_from_html(html):
    """Extract and return text from HTML"""
    soup = BeautifulSoup(html, 'html5lib')
    text = soup.get_text()
    return text


def get_page(url):
    """Get text and JPEG image of the web page at URL. Returns a tuple of text and base64-encoded image"""
    params = {'url': url, 'html': 1, 'jpeg': 1, 'render_all': 1, 'wait': 0.1}
    r = requests.get(splash_endpoint + "/render.json", params=params)
    resp_dict = r.json()
    html = resp_dict.get('html')
    image = resp_dict.get('jpeg')
    text = get_text_from_html(html)
    return text, image


def _strip_text(text):
    """Strips whitespace from a string and converts to lower-case for comparison with another string.
    """
    return re.sub("\s*", "", text.lower())


def check(url, search_text):
    """Checks if search_text is on URL, returns tuple of boolean and base64-encoded JPEG image of page"""
    page_text, page_image = get_page(url)
    return _strip_text(search_text) in _strip_text(page_text), page_image

print(check('http://blog.c-mart.in', 'ham sandwich'))
