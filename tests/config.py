import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class TestConfig(object):
    SERVICE_NAME = 'familysnap-api'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ecd173cf24c19be30f567ea79095c56d'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, SERVICE_NAME + '.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ['en', 'ZH-cn']

    JWT_SECRET_KEY = "8z961vbqEgSEiNH08vc_ig"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=10)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # SMS/OTP setting
    OTP_EXPIRATION = 10             # 10 minutes
    OTP_DIGITS = 6
    SMS_VENDOR = 'twillio'          # twillio, uni-sms or tencent

    # Twillio SID and Authe token
    TWILIO_ACCOUNT_SID = 'twilio_account_sid'
    TWILIO_AUTH_TOKEN = 'twilio_auth_token'
    TWILIO_SMS_SID = 'twilio_sms_sid'

    # Uni-SMS Access Key ID
    UNISMS_ACCESSKEY_ID = 'unisms_test_key'
    UNISMS_SIGNATURE = 'my signature'

    # Uni-SMS Access Key ID
    TENCENT_SECRET_ID = 'tencent_secret_id'
    TENCENT_SECRET_KEY = 'tencent_secret_key'
    TENCENT_SDK_APPID = 'sdk_appid'
    TENCENT_TEMPLATE_ID = 'template_id'
    TENCENT_SENDER_ID = 'senderId'
    TENCENT_APP_NAME = 'myapp'
