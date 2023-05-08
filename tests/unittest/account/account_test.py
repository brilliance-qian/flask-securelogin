import pytest
from unittest.mock import Mock, patch

from tests.app import test_app

from flask_securelogin.exception import AppException
from flask_securelogin.account import AccountManager
from flask_securelogin.sms.SMSFactory import SMSFactory
from flask_securelogin.sms.OTPGenerator import OTPGenerator
from flask_securelogin.models import User
from flask_securelogin import secure_auth

from tests.mockups.sms.SimulatorClient import SimulatorClient


class TestAppException(AppException):
    def __init__(self, error):
        super().__init__("", error, "")


class TestAccountManager:
    def test_account_creation_w_password(self, test_app):
        config = test_app.config

        username = "test_account_case1"
        email = "test_account_case1@abc.com"
        password = "duzzy"

        manager = AccountManager(secure_auth.db, config)
        new_user = manager.create_user_w_password(username, email, password)

        assert new_user.username == username
        assert new_user.email == email
        assert new_user.status == 'active'
        assert new_user.check_password(password)
        assert new_user.time_created is not None

        user = User.query.filter_by(email=email).first()
        assert new_user == user

    def test_account_creation_w_phone(self, test_app):
        config = test_app.config

        username = "test_account_case1"
        phone = "+180192303"

        manager = AccountManager(secure_auth.db, config)
        new_user = manager.create_user_w_phone(username, phone)

        assert new_user.username == username
        assert new_user.phone == phone
        assert new_user.status == 'active'
        assert new_user.time_created is not None

        user = User.query.filter_by(phone=phone).first()
        assert new_user == user

    @pytest.mark.parametrize(("mock_user", "mock_email", "expected_exception"),
      [
       (User(email='t1@mytest.com', status='active', auth_type='PASSWORD'), 't1@mytest.com', None),
       (None, 't1@mytest.com', TestAppException("AccountNotExist")),
       (User(email='t1@mytest.com', status='closed', auth_type='PASSWORD'), 't1@mytest.com',
        TestAppException("AccountInactive")),
       (User(email='t1@mytest.com', status='active', auth_type='PHONE'), 't1@mytest.com',
        TestAppException("AccountInvalidAuthType"))
      ],)
    def test_login_by_password(self, test_app, mock_user, mock_email,
              expected_exception, mocker):
        config = test_app.config

        password = "duzzy"
        if mock_user is not None:
            mock_user.set_password(password)    # ensure password check is always correct

        mock_sqlalchemy = mocker.patch("flask_sqlalchemy.model._QueryProperty.__get__")
        mock_sqlalchemy.return_value.filter_by.return_value.first.return_value = mock_user

        exception = None
        try:
            manager = AccountManager(secure_auth.db, config)
            manager.login_by_password(mock_email, password)
        except AppException as e:
            exception = e

        if exception is not None and expected_exception is not None:
            assert exception.error == expected_exception.error
        else:
            assert exception == expected_exception

    @pytest.mark.parametrize(("mock_user", "mock_phone", "expected_exception"),
      [
       (None, '+14090801100', TestAppException("AccountNotExist")),
       (User(phone='+188940', status='closed', auth_type='PHONE'), '+188940', TestAppException("AccountInactive")),
       (User(email='t1@mytest.com', phone='+8610891201', status='active', auth_type='PASSWORD'), '+8610891201',
        TestAppException("AccountInvalidAuthType"))
      ],)
    def test_failure_login_by_phone(self, test_app, mock_user, mock_phone,
              expected_exception, mocker):
        config = test_app.config

        mock_sqlalchemy = mocker.patch("flask_sqlalchemy.model._QueryProperty.__get__")
        mock_sqlalchemy.return_value.filter_by.return_value.first.return_value = mock_user

        exception = None
        try:
            manager = AccountManager(secure_auth.db, config)
            manager.login_by_phone(mock_phone)
        except AppException as e:
            exception = e

        if exception is not None and expected_exception is not None:
            assert exception.error == expected_exception.error
        else:
            assert exception == expected_exception

    @pytest.mark.parametrize(("mock_user", "mock_phone", "mock_token_sent", "mock_token_recv", "expected_exception"),
      [
       (User(phone='+8610891201', status='active', auth_type='PHONE'), '+8610891201', "000000",
        "123456", TestAppException("SMSVerifyFailure")),
       (User(phone='+8610891201', status='active', auth_type='PHONE'), '+8610891201', "123456",
        "123456", None)
      ],)
    def test_login_verify_sms(self, test_app, mock_user, mock_phone,
           mock_token_sent, mock_token_recv, expected_exception, mocker):
        config = test_app.config

        mock_sqlalchemy = mocker.patch("flask_sqlalchemy.model._QueryProperty.__get__")
        mock_sqlalchemy.return_value.filter_by.return_value.first.return_value = mock_user

        mocker.patch(__name__ + ".SMSFactory.create_instance", return_value=SimulatorClient(secure_auth.db, config))
        mocker.patch(__name__ + ".OTPGenerator.generate_otp", return_value=mock_token_sent)

        exception = None
        manager = AccountManager(secure_auth.db, config)
        user = manager.login_by_phone(mock_phone)
        assert user == mock_user

        try:
            manager.login_verify_sms(mock_phone, mock_token_recv)
        except AppException as e:
            exception = e

        if exception is not None and expected_exception is not None:
            assert exception.error == expected_exception.error
        else:
            assert exception == expected_exception
