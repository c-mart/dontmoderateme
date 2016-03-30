import pytest
from pytest import fixture
import dontmoderateme
import dontmoderateme.models as models
from dontmoderateme import db


@fixture
def setup():
    """Set up each test: initialize test client and database, disable rate limiter."""
    dontmoderateme.app.config.from_object('dontmoderateme.config_test')
    app = dontmoderateme.app.test_client()
    dontmoderateme.db.create_all()
    dontmoderateme.limiter.enabled = False


@fixture
def teardown():
    """Empty the database as cleanup after each test"""
    dontmoderateme.db.session.remove()
    dontmoderateme.db.drop_all()


def test_testing_test():
    assert True

if __name__ == '__main__':
    pytest.main()