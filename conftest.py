import pytest
import dontmoderateme

@pytest.fixture
def app():
    app = dontmoderateme.app
