from flask import Blueprint
from flask_jwt_extended import JWTManager


class SecureAuth:
    def __init__(self):
        self.bp = Blueprint('auth', __name__)
        self.jwt = JWTManager()
        return

    def init_db(self, db):
        self.db = db

    def init_app(self, app):
        self.app = app

        # initialize jwt and bp
        self.jwt.init_app(app)
        app.register_blueprint(self.bp, url_prefix='/api')
