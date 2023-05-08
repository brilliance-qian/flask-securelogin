import pytest
import logging
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from tests.config import TestConfig
from flask_securelogin import secure_auth

db = SQLAlchemy()
migrate = Migrate()
secure_auth.init_db(db)


def create_app(config_class):
    app = Flask(__name__, static_folder=None, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    secure_auth.init_app(app)

    app.logger.setLevel(logging.INFO)

    return app


@pytest.fixture
def test_app():
    app = create_app(TestConfig)
    app.testing = True

    with app.app_context():
        db.create_all()

        yield app  # this is where the testing happens!
        db.drop_all()
