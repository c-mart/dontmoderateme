import pytest
from pytest import fixture, yield_fixture
import dontmoderateme
import dontmoderateme.models as models
from dontmoderateme import db
from dontmoderateme import mail
import re


@yield_fixture
def app():
    """Set up each test: initialize test client and database, disable rate limiter, return test client."""
    app = dontmoderateme.app
    app.config.from_object('dontmoderateme.config_test')
    db.create_all()
    dontmoderateme.limiter.enabled = False
    yield app
    db.session.remove()
    db.drop_all()


@fixture
def populate_db():
    """Populate database with a test user"""
    testuser = models.User('test@test.com', 'testtest', activated=True)
    db.session.add(testuser)
    db.session.commit()


def test_home_page(app):
    r = app.test_client().get('/')
    assert b"Get notified when your online posts are removed." in r.get_data()
    

class TestNewAccountWorkflow:
    """Tests new account registration, activation, and login process"""

    def test_registration_form(self, app):
        with app.app_context():
            with mail.record_messages() as outbox:
                r = app.test_client().post('/register', follow_redirects=True, data=dict(email='testy@mctester.son',
                                                                                         password='ilovelucy',
                                                                                         confirm_password='ilovelucy'))
                assert b"Activate Account" in r.get_data(), "Should see account activation instructions"
                email = outbox[0]
                assert email.recipients[0] == 'testy@mctester.son'
                assert "Activate your account" in email.subject
                assert "Please visit this page to activate your account" in email.body
                assert "Please click this link to activate your account" in email.html
                url = re.search('http://.*/activate\?code=(.*)$', email.body)
                assert 'http://' in url.group(0) and '/activate?code=' in url.group(0), \
                    "Should see activation URL in email"
                code = url.group(1)
                return code

    def test_account_activation(self, app):
        """Tests account activation. Builds on previous test_registration_form"""
        code = self.test_registration_form(app)
        r = app.test_client().get('/activate?code=' + code, follow_redirects=True)
        assert b"your account has been activated" in r.get_data()

    def test_login_new_account(self, app):
        """Tests new account login after register + activation process. Builds on previous test_account_activation"""
        self.test_account_activation(app)
        r = app.test_client().post('/login', follow_redirects=True, data=dict(email='testy@mctester.son',
                                                                              password='ilovelucy'))
        assert b"Logged in as testy@mctester.son" in r.get_data(), "Should be able to log in as new account"


def test_login(app, populate_db):
    r = app.test_client().post('/login', follow_redirects=True, data=dict(email='test@test.com', password='testtest'))
    assert b"Logged in as test@test.com" in r.get_data(), "Should see logged in notice"

if __name__ == '__main__':
    pytest.main()