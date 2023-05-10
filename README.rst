*******************
flask-securelogin
*******************

Description
############
Flask-securelogin is a library providing flask-based REST API services for account authentication with strong security protection.

When developers build a service for mobile app or for web, one important thing they have to consider is to build an authentication for their customers. Most developers would choose password-based login design and session-cooke-based authentication because it is easy to implement.

Unfortunately password-based authentication is a vulnerable design. Their customers could be victims of many security attacks: brutal force attack, phishing attack, password-leak if the web service didn't design their account security protection carefully. Besides, password-based authentciation is also a hassle to customers. For better security, the web service provider usually would ask their customers to have a complex password that must be 12+ charactors long and is with combination of uppercase, lowercase letters, digits and special charactors. This kind of password is usally hard to remember. Some customers might write it down somewhere, which is not a good approach on account security. Some customers might use a same password across many websites as people may have accounts on dozens of websites and it is hard to keep and remember different password per website. This is also not a good approach on account security. To enhance the security, many websites then ask their customers to provide multiple-factor-authentication (MFA), which make the system complicated and the login process less user friendly. Besides, account recovery from forget-password is also a painful process for customers.

Flask-securelogin provides a SMS-based passwordless authentication. The phone number is the customer's userid. After registration, when a customer is trying to login, just enter the phone number. The flask-securelogin sends SMS/OTP code to the customer. After SMS verification, the authentication is done. No password. No worry about phishing attack, brutal force attack or password leak. No worry about forgetting password. Concise and secure.

Installation
############
To install the latest release on `PyPI <https://pypi.org/project/flask-securelogin/>`_,
simply run:
::
  pip3 install flask-securelogin
Or to install the latest development version, run:
::
  git clone git@github.com:brilliance-qian/flask-securelogin.git
  cd flask-securelogin
  python3 setup.py install
  
Quick Tutorial
################
Flask-securelogin provides a set of authentication APIs that can be seamlessly integrated to your REST API service. In your flask application, just simply add a few lines then the whole set of APIs will be ready to support account registration and login.

Setup
******
Create the environment
::
  $ mkdir sample_api
  $ cd sample_api
  $ python3 -m venv venv
  $ source venv/bin/activate
  $ pip install flask-securelogin
  $ pip freeze > requirements.txt
  $ mkdir app
  
Source Code
************
Directory tree structure
::
    sample_api
    ├── app
    │   ├── __init__.py
    │   └── routes.py
    ├── entry.py
    ├── config.py
    └── tests
        └── test_routes.py
        
app/__init__.py
::
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate
    from flask_securelogin import secure_auth
    from config import Config

    db = SQLAlchemy()
    secure_auth.init_db(db)
    migrate = Migrate()

    def create_app(config_class=Config):
        app = Flask(__name__, static_folder=None, instance_relative_config=True)
        app.config.from_object(config_class)

        db.init_app(app)
        migrate.init_app(app, db)

        secure_auth.init_app(app)

        app.logger.setLevel(logging.INFO)

        return app
  
app/routes.py
::
    from flask_securelogin import routes
    from flask_securelogin.sms.TwilioClient import TwilioClient

    @secure_auth.create_sms_service
    def create_sms_service_instance(db, config, phone):
        return TwilioClient(db, config)
    
entry.py
::
    from app import create_app, db
    from app import routes
    from flask_securelogin.models import User

    app = create_app()

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User}
        
config.py, which is used to specify SMS vendor's setting
::
    import os
    import traceback
    import bcrypt
    from datetime import timedelta

    basedir = os.path.abspath(os.path.dirname(__file__))

    class Config(object):
        SERVICE_NAME = 'mysite'
        SECRET_KEY = os.environ.get('SECRET_KEY') or '0122f9b60974f7dc71924f8c'
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, SERVICE_NAME + '.db')

        SQLALCHEMY_TRACK_MODIFICATIONS = False

        JWT_SECRET_KEY = bcrypt.hashpw(b'FkGkIShuf4Mk40illonZJA', bcrypt.gensalt())
        JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=10)
        JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=60)

        # SMS/OTP setting
        OTP_EXPIRATION = 10             # 10 minutes
        OTP_DIGITS = 6

        # Twillio SID and Authe token
        TWILIO_ACCOUNT_SID = 'account_sid' # get your account sid from Twillio
        TWILIO_AUTH_TOKEN = 'auth_token'   # get your auth_token from Twillio
        TWILIO_SMS_SID = 'sms_sid'         # get your sms_sid from Twillio
        
        
.flaskenv
::
    #.flaskenv
    FLASK_APP=entry.py
    FLASK_DEBUG=1

Validation
************

After the code is done, run the commands below to initialize 
::
    $ flask db init
    $ flask db migrate
    $ flask db upgrade
    
Validate the auth routes
::
    $ flask routes
    Endpoint                        Methods  Rule
    ------------------------------  -------  -----------------------------------
    auth.change_password            POST     /api/auth/password
    auth.login                      POST     /api/auth/login_sms
    auth.login                      POST     /api/auth/login
    auth.logout                     POST     /api/auth/logout
    auth.logout_all_other_sessions  POST     /api/auth/logout_all_other_sessions
    auth.op                         POST     /api/auth/op
    auth.op2                        POST     /api/auth/op2
    auth.refresh                    POST     /api/auth/refresh
    auth.register                   POST     /api/auth/register
    auth.verify_sms                 POST     /api/auth/verify_sms
    
Test
************

