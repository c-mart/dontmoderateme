import unittest
import dontmoderateme
import dontmoderateme.models as models
from dontmoderateme import db as db
from datetime import datetime


class dontmoderatemeTestCase(unittest.TestCase):

    def setUp(self):
        """Set up each test: initialize test client and database, disable rate limiter."""
        dontmoderateme.app.config.from_object('dontmoderateme.config_test')
        self.app = dontmoderateme.app.test_client()
        dontmoderateme.db.create_all()
        dontmoderateme.limiter.enabled = False

    def tearDown(self):
        """Empty the database as cleanup after each test"""
        dontmoderateme.db.session.remove()
        dontmoderateme.db.drop_all()

    test_user_email = 'test@test.com'
    test_user_password = 'test'

    # Helper Methods

    def login(self, email=test_user_email, password=test_user_password):
        """Logs test user in."""
        return self.app.post('/login', data=dict(email=email, password=password), follow_redirects=True)

    def logout(self):
        """Logs test user out."""
        return self.app.get('/logout', follow_redirects=True)

    def create_user(self,
                    email='test@test.com',
                    password='test',
                    activated=True):
        """Create and return a user object"""
        user = models.User(email, password, activated)
        db.session.add(user)
        db.session.commit()
        return user

    def create_monitor(self,
                       user_id=None,
                       url='http://smogdemo.c-mart.in',
                       text='Lorem ipsum dolor sit amet, consectetur adipiscing elit.'):
        """Create and return a monitor object"""
        monitor = models.Monitor(user_id=user_id or self.create_user(self).id, url=url, text=text)
        db.session.add(monitor)
        db.session.commit()
        return monitor

    def create_check(self,
                     monitor_id=None,
                     result=True,
                     timestamp=None):
        """Create and return a check object"""
        check = models.Check(monitor_id=monitor_id or self.create_monitor(self).id, result=result, timestamp=timestamp)
        db.session.add(check)
        db.session.commit()
        return check

    # Database schema test cases

    def test_db_relationships(self):
        """Create related database objects and ensure the relationships work"""
        my_user = self.create_user()
        my_monitor = self.create_monitor(user_id=my_user.id)
        my_check = self.create_check(monitor_id=my_monitor.id)

        assert my_user is models.User.query.first(), 'Should see queried user'
        assert my_monitor.user is my_user, 'Monitor object should refer to user'
        assert my_check.monitor is my_monitor, 'Check object should refer to monitor'
        assert my_user.monitors.first() is my_monitor, 'User object should refer to monitor'
        assert my_monitor.checks.first() is my_check, 'Monitor object should refer to checks'

    def test_changed_check(self):
        raise NotImplementedError

    def test_create_monitor(self):
        """Creates test monitor."""
        raise NotImplementedError