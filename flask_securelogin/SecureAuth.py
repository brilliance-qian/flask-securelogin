from typing import Callable
from flask import Blueprint
from flask_jwt_extended import JWTManager


class SecureAuth:
    """
    An object used to hold the context setting and callback functions for flask_securelogin
    """
    def __init__(self) -> None:
        """
        Create the SecureAuth instance. The instance contains
        - Blueprint object to dispatch Rest API
        - JWTManager object to manage access token and refresh token
        """
        self.bp = Blueprint('auth', __name__)
        self.jwt = JWTManager()
        self._create_sms_service_handler = None
        self._check_if_access_token_revoked_hanlder = None
        return

    def init_db(self, db) -> None:
        """
        Initialize the SecureAuth instance with database object. The DB object is used
        to insert/update/query DB for internal data models like User, ActiveToken

        :param db:
            An object of SQLAlchemy instance
        """
        self.db = db

        return

    def init_app(self, app) -> None:
        """
        Initialize the SecureAuth instance with a flask app object.

        :param app:
            An object of flask app
        """
        self.app = app

        # initialize jwt and bp
        self.jwt.init_app(app)
        app.register_blueprint(self.bp, url_prefix='/api')

        return

    def create_sms_service(self, callback: Callable) -> Callable:
        """
        This decorator sets callback function for creating sms service. The callback
        function will be used when it requests to create a service to send sms through
        external vendors.

        The decorated function must take 3 parameters.

        The first parameter is the db object that was initialized by init_db
        The second parameter is a dictionary containing configurations
        The third parameter is a string of phone number. The callback function can
        create different sms services per phone number country

        The decorated function must return an instance derived from SMSCall
        """
        self._create_sms_service_handler = callback
        return callback

    def get_create_sms_service_handler(self) -> Callable:
        """
        The function is to get the decorator function of create_sms_service.
        It is for internal use.
        """
        return self._create_sms_service_handler

    def check_if_access_token_revoked(self, callback: Callable) -> Callable:
        """
        This decorator sets callback function for checking whether access token is revoked.

        Usually an access token expires very soon. You don't have to implement this decorator.
        And implementation of checking access token will increase latency for every api
        request. However, if your application needs a better security and can tolerate the
        latency increase, you can implement this decorator. If you do so, it is strongly suggested
        that cache is used to store and check the access token.

        The decorated function must take 1 parameter.

        The first parameter is the jti of the access token.

        The decorated function must return Boolean. True means the token is revoked and invalid,
        false means token is not revoked and still valid.
        """
        self._check_if_access_token_revoked_hanlder = callback
        return callback

    def get_check_if_access_token_revoked_handler(self) -> Callable:
        """
        The function is to get the decorator function of check_if_access_token_revoked.
        It is for internal use.
        """
        return self._check_if_access_token_revoked_hanlder
