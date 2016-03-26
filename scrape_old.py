from datetime import datetime
import dryscrape
from os import path
import re
import sys
import slugify
from bs4 import BeautifulSoup

if 'linux' in sys.platform:
    # start xvfb in case no X is running. Make sure xvfb
    # is installed, otherwise this won't work!
    dryscrape.start_xvfb()


def _strip_text(text):
    """Strips whitespace from a string and converts to lower-case for comparison with another string.
    """
    return re.sub("\s*", "", text.lower())


def get_text_on_page(url):
    """Returns string of text on web page specified by url.
    """
    sess = dryscrape.Session()
    sess.set_attribute('auto_load_images', False)
    sess.visit(url)
    html = sess.body()
    soup = BeautifulSoup(html, 'html5lib')
    text = soup.get_text()
    return text


def is_text_on_page(search_text, url):
    """Determines whether text is present on url.
    Returns boolean.
    """
    url_text = get_text_on_page(url)
    return _strip_text(search_text) in _strip_text(url_text)


def render_png(url, file_path=None):
    """Renders a .PNG image of web page specified by url.
    Image will be saved in current directory unless a file path is specified by path keyword argument.
    """
    sess = dryscrape.Session()
    sess.visit(url)
    filename = path.join(file_path if file_path is not None else '', slugify.slugify(url) + '_' + datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S") + '.png')
    return sess.render(filename)