import pytest
from tests.app import create_app, db  # tests.app must imported prior to routes for db initalization
from flask_securelogin import routes  # noqa: F401 # pylint:disable=unused-import
from flask_securelogin import secure_auth

from tests.config import TestConfig


@pytest.fixture
def client():
    app = create_app(TestConfig)
    app.testing = True

    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client  # this is where the testing happens!
        db.drop_all()
