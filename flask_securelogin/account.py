from datetime import datetime, timezone
from flask_securelogin.exception import AppException

from flask_securelogin.models import User
from flask_securelogin.sms.SMSFactory import SMSFactory

import uuid


class AccountManager():
    def __init__(self, db, config=None):
        self._db = db
        self._config = config

    def create_user_w_password(self, username, email, password):
        # check whether the user already exists
        user = User.query.filter_by(email=email).first()
        if user is not None and user.status != 'closed':
            raise AppException("AccountCreationFailure", "AccountAlreadyExist",
                               "failed to create an account as the email already exists")

        # create a new user
        new_user = User(public_id=str(uuid.uuid4()), username=username, auth_type='PASSWORD')
        new_user.email = email
        new_user.set_password(password)

        new_user.status = 'active'
        new_user.time_created = int(datetime.now(timezone.utc).timestamp())

        self._db.session.add(new_user)
        self._db.session.commit()

        return new_user

    def create_user_w_phone(self, username, phone):
        # check whether the user already exists
        user = User.query.filter_by(phone=phone).first()
        if user is not None and user.status != 'closed':
            raise AppException("AccountCreationFailure", "AccountAlreadyExist",
                               "failed to create an account as the phone already exists")

        # create a new user
        new_user = User(public_id=str(uuid.uuid4()), username=username, auth_type='PHONE')
        new_user.phone = phone

        new_user.status = 'active'
        new_user.time_created = int(datetime.now(timezone.utc).timestamp())

        self._db.session.add(new_user)
        self._db.session.commit()

        return new_user

    def account_sanity_check(self, user, auth_type):
        if user is None:
            raise AppException("LoginFailure", "AccountNotExist", "the user doesn't exist")

        if user.auth_type != auth_type:
            raise AppException("LoginFailure", "AccountInvalidAuthType", "authentication method doesn't match")

        if user.status != 'active':
            raise AppException("LoginFailure", "AccountInactive", "the user account is not active anymore")

        return

    def login_by_password(self, email, password):
        user = User.query.filter_by(email=email).first()
        self.account_sanity_check(user, 'PASSWORD')

        if not user.check_password(password):
            raise AppException("LoginFailure", "AccountInvalidPassword", "wrong password")

        return user

    def login_by_phone(self, phone):
        user = User.query.filter_by(phone=phone).first()
        self.account_sanity_check(user, 'PHONE')

        sms = SMSFactory.create_instance(self._db, self._config, phone)
        if not sms.send_sms(phone):
            raise AppException("LoginFailure", "SMSSendFailure", "can't send sms code due to system failure")

        return user

    def login_verify_sms(self, phone, token):
        user = User.query.filter_by(phone=phone).first()
        self.account_sanity_check(user, 'PHONE')

        sms = SMSFactory.create_instance(self._db, self._config, phone)
        if not sms.verify_sms(phone, token):
            raise AppException("LoginFailure", "SMSVerifyFailure", "incorrect sms code")

        return user

    def change_password(self, userid, oldpassword, newpassword):
        user = User.query.filter_by(id=userid).first()
        self.account_sanity_check(user, user.auth_type)

        if not user.check_password(oldpassword):
            raise AppException("PasswordFailure", "ChangePasswordFailed", "password is not correct")

        user.set_password(newpassword)

        self._db.session.commit()
