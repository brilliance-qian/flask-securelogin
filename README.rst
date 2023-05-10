Flask-securelogin
====================

Flask-securelogin is a library providing flask-based REST API services for account authentication with strong security protection.

When developers build a service for mobile app or for web, one important thing they have to consider is to build an authentication for their customers. Most developers would choose password-based login design and session-cooke-based authentication because it is easy to implement.

Unfortunately password-based authentication is a vulnerable design. Their customers could be victims of many security attacks: brutal force attack, phishing attack, password-leak if the web service didn't design their account security protection carefully. Besides, password-based authentciation is also a hassle to customers. For better security, the web service provider usually would ask their customers to have a complex password that must be 12+ charactors long and is with combination of uppercase, lowercase letters, digits and special charactors. This kind of password is usally hard to remember. Some customers might write it down somewhere, which is not a good approach on account security. Some customers might use a same password across many websites as people may have accounts on dozens of websites and it is hard to keep and remember different password per website. This is also not a good approach on account security. To enhance the security, many websites then ask their customers to provide multiple-factor-authentication (MFA), which make the system complicated and the login process less user friendly. Besides, account recovery from forget-password is also a painful process for customers.

Flask-securelogin provides a SMS-based passwordless authentication. The phone number is the customer's userid. After registration, when a customer is trying to login, just enter the phone number. The flask-securelogin sends SMS/OTP code to the customer. After SMS verification, the authentication is done. No password. No worry about phishing attack, brutal force attack or password leak. No worry about forgetting password. Concise and secure.

Installation
====================
To install the latest release on `PyPI <https://pypi.org/project/flask-securelogin>`_ 

simply run:

.. code:: text

    pip3 install flask-securelogin

Or to install the latest development version, run:

.. code:: text

    git clone git@github.com:brilliance-qian/flask-securelogin.git
    cd flask-securelogin
    python3 setup.py install
  
Quick Tutorial
====================
Flask-securelogin provides a set of authentication APIs that can be seamlessly integrated to your REST API service. In your flask application, just simply add a few lines then the whole set of APIs will be ready to support account registration and login.

Setup
--------
Create the environment

.. code:: text
  
  $ mkdir sample_api
  $ cd sample_api
  $ python3 -m venv venv
  $ source venv/bin/activate
  $ pip install flask-securelogin
  $ pip freeze > requirements.txt
  $ mkdir app
  
Source Code
------------
Directory tree structure

.. code:: text

    sample_api
    ├── app
    │   ├── __init__.py
    │   └── routes.py
    ├── entry.py
    ├── config.py
    └── tests
        └── test_routes.py
        
app/__init__.py

.. code:: python

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

.. code:: python

    from flask_securelogin import routes
    from flask_securelogin import secure_auth
    from flask_securelogin.sms.TwilioClient import TwilioClient

    @secure_auth.create_sms_service
    def create_sms_service_instance(db, config, phone):
        return TwilioClient(db, config)
    
entry.py

.. code:: python

    from app import create_app, db
    from app import routes
    from flask_securelogin.models import User

    app = create_app()

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User}
        
config.py, which is used to specify SMS vendor's setting

.. code:: python

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

.. code:: python

    #.flaskenv
    FLASK_APP=entry.py
    FLASK_DEBUG=1

Validation
------------

After the code is done, run the commands below to initialize 

.. code:: text

    $ flask db init
    $ flask db migrate
    $ flask db upgrade
    
Validate the auth routes

.. code:: text

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
------------
Before you start to test SMS-based authentication, you need to setup configuration for calling SMS vendor. In this example, I suggest Twilio as the vendor. Twilio provides free trial account for testing purpose. After you create a free trial account on Twillio, register and verify your phone number on the free trial acount, the phone number can be used for testing without charge. Copy the Twilio account SID, auth token and SMS SID from Twilio, update the info in config.py. You are good to go.

For details about how to create free trial account and get account SID, auth token and SMS SID, please refer to `create your free trial account`_

.. _create your free trial account: https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account

After Twilio service is setup, let test the SMS-based authentication

Open a terminal Run the API server

.. code:: text

    $ cd sample_api
    $ source venv/bin/activate
    $ flask run
     * Serving Flask app 'entry.py'
     * Debug mode: on
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
     * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: 633-717-714


Open another terminal, try below commands
Create a test account

Registration API ``/api/auth/register``

.. code:: text
   
    $ curl -X POST -d '{ "username": "my test account", "auth_type": "PHONE", "phone": <YOUR_PHONE_NUMBER>}' -H "content-type: application/json" http://127.1:5000/api/auth/register
    {
      "message": "registered successfully",
      "userid": "e5b53d55-bb32-40fb-aaeb-8ad750158639"
    }
    
Login with the test account

Login API ``/api/auth/login``

.. code:: text

    $ curl -X POST -d '{ "auth_type": "PHONE", "phone":  <YOUR_PHONE_NUMBER> }' -H "content-type: application/json" http://127.1:5000/api/auth/login
    {
      "phone":  <YOUR_PHONE_NUMBER>,
      "userid": "e5b53d55-bb32-40fb-aaeb-8ad750158639"
    }
    
It receives a response with phone number and userid. Meanwhile, a SMS code is sent to your phone by Twilio. 

If you didn't set Twilio settings correctly in config.py, you would receive below response

.. code:: text

    {
      "error": "TwilioRestException",
      "exception": {
        "exception": "NoneType",
        "message": "None"
      },
      "http_code": "Bad Request",
      "message": "\n\u001b[31m\u001b[49mHTTP Error\u001b[0m \u001b[37m\u001b[49mYour request was:\u001b[0m\n\n\u001b[36m\u001b[49mPOST /Services/sms_sid/Verifications\u001b[0m\n\n\u001b[37m\u001b[49mTwilio returned the following information:\u001b[0m\n\n\u001b[34m\u001b[49mUnable to create record: Authentication Error - invalid username\u001b[0m\n\n\u001b[37m\u001b[49mMore information may be available here:\u001b[0m\n\n\u001b[34m\u001b[49mhttps://www.twilio.com/docs/errors/20003\u001b[0m\n\n"
    }

Next step, enter the phone, userid and SMS token in the API below to verify SMS.

Verify SMS API ``/api/auth/verify_sms``

.. code:: text

    $ curl -X POST -d '{ "userid": "e5b53d55-bb32-40fb-aaeb-8ad750158639", "phone":  <YOUR_PHONE_NUMBER>, "token": <TOKEN> }' -H "content-type: application/json" http://127.1:5000/api/auth/verify_sms
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6dHJ1ZSwiaWF0IjoxNjgzNjkwNzY3LCJqdGkiOiI0ZmViZTI5Zi04YjRkLTQ1ZmMtOTc5Ni1iMjFmZTA0ZmRkOTYiLCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoxLCJuYmYiOjE2ODM2OTA3NjcsImV4cCI6MTY4MzY5MTM2N30.1US8-ndM3S-wrjSz8I9XOyBjvTPAjs_CVCrPZowGMeQ",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4MzY5MDc2NywianRpIjoiNmQ2ZjNkMmMtMDEyNC00OTA2LThjYjAtMTFjMTA5Mzg0NWU3IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOjEsIm5iZiI6MTY4MzY5MDc2NywiZXhwIjoxNjg4ODc0NzY3LCJzaWQiOiI1YWUwOWViMy03NTNlLTQ5NDYtYmNhZS0yN2UzNzk4NDVlOGYifQ.OXCMMmy9xn8-UooJVlnnCBFEd0s9MoXAx_z8q2O9RqQ",
      "userid": "e5b53d55-bb32-40fb-aaeb-8ad750158639"
    }
    
Now the SMS authentication is done. You received an access token and refresh token. Access token is used to call protected operations in the API server. Refresh token is used to refresh access token if the access token is expired.
 
Call protected operations with the access token. After you create your own operation, you can replace it by yours.

Operation API ``/api/auth/op``

.. code:: text

    $ curl -X POST -d '{}' -H "content-type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6dHJ1ZSwiaWF0IjoxNjgzNjkwNzY3LCJqdGkiOiI0ZmViZTI5Zi04YjRkLTQ1ZmMtOTc5Ni1iMjFmZTA0ZmRkOTYiLCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoxLCJuYmYiOjE2ODM2OTA3NjcsImV4cCI6MTY4MzY5MTM2N30.1US8-ndM3S-wrjSz8I9XOyBjvTPAjs_CVCrPZowGMeQ" http://127.1:5000/api/auth/op
    {
      "message": "test op successful"
    }

Refresh token(please be reminded refresh token is used in Authorization header)

Refresh token API ``/api/auth/refresh``

.. code:: text

    $ curl -X POST -d '{}' -H "content-type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4MzY5MDc2NywianRpIjoiNmQ2ZjNkMmMtMDEyNC00OTA2LThjYjAtMTFjMTA5Mzg0NWU3IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOjEsIm5iZiI6MTY4MzY5MDc2NywiZXhwIjoxNjg4ODc0NzY3LCJzaWQiOiI1YWUwOWViMy03NTNlLTQ5NDYtYmNhZS0yN2UzNzk4NDVlOGYifQ.OXCMMmy9xn8-UooJVlnnCBFEd0s9MoXAx_z8q2O9RqQ" http://127.1:5000/api/auth/refresh
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4MzY5MTI5NCwianRpIjoiM2QxZTMxMjUtY2RlNC00MDkzLTgxMWQtYWNjZmZmNGIzZjUxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNjgzNjkxMjk0LCJleHAiOjE2ODM2OTE4OTR9.0klw7uayU9qKh7fIEnhON6nrQdqFh1bbiF7mfnKOrJU",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4MzY5MTI5NCwianRpIjoiNDk1ZDdmMjQtNTU0Yy00NjM3LWE5NzYtMzJmNDFlNDMzNzI3IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOjEsIm5iZiI6MTY4MzY5MTI5NCwiZXhwIjoxNjg4ODc1Mjk0LCJzaWQiOiI1YWUwOWViMy03NTNlLTQ5NDYtYmNhZS0yN2UzNzk4NDVlOGYifQ.UmNLBPuguHrGtsrJqNhp4TWgmu0OvORvEL58ittBgRc"
    }
    
Logout API ``/api/auth/logout``

.. code:: text

    $ curl -X POST -d '{ "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4MzY5MTI5NCwianRpIjoiNDk1ZDdmMjQtNTU0Yy00NjM3LWE5NzYtMzJmNDFlNDMzNzI3IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOjEsIm5iZiI6MTY4MzY5MTI5NCwiZXhwIjoxNjg4ODc1Mjk0LCJzaWQiOiI1YWUwOWViMy03NTNlLTQ5NDYtYmNhZS0yN2UzNzk4NDVlOGYifQ.UmNLBPuguHrGtsrJqNhp4TWgmu0OvORvEL58ittBgRc"}' -H "content-type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4MzY5MTI5NCwianRpIjoiM2QxZTMxMjUtY2RlNC00MDkzLTgxMWQtYWNjZmZmNGIzZjUxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNjgzNjkxMjk0LCJleHAiOjE2ODM2OTE4OTR9.0klw7uayU9qKh7fIEnhON6nrQdqFh1bbiF7mfnKOrJU"  http://127.1:5000/api/auth/logout
    {
      "message": "logout successful"
    }
