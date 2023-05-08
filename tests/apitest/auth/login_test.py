import pytest
import json
import flask
from types import SimpleNamespace

from tests.app import db
from flask_securelogin.sms.SMSFactory import SMSFactory   # noqa: F401 # pylint:disable=unused-importt
from flask_securelogin.sms.OTPGenerator import OTPGenerator   # noqa: F401 # pylint:disable=unused-importt

from tests.apitest.client import client   # noqa: F401 # pylint:disable=unused-importt
from tests.mockups.sms.SimulatorClient import SimulatorClient


class TestLogin:
    @pytest.fixture()
    def account_pwd(self, client):
        account = {'username': 'login test name1', 'auth_type': 'PASSWORD',
                    'email': 'abc1@logintest.com', 'password': 'abc123'}
        res = client.post('/api/auth/register',
                data=json.dumps(account),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"

        userid = d.userid
        access_token = d.access_token
        refresh_token = d.refresh_token
        return (userid, access_token, refresh_token)

    @pytest.mark.parametrize(("email", "password", "status_code"),
       [('abc1@logintest.com', 'abc123', 200),
         ('abc1@logintest.com', 'yuxz12', 400)
       ])
    def test_login_pwd(self, client, email, password, status_code, account_pwd):
        data = {'email': email, 'password': password, 'auth_type': 'PASSWORD'}
        res = client.post("/api/auth/login",
                data=json.dumps(data),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == status_code, f"response code: {res.status_code}, message: {d}"

    @pytest.mark.parametrize(("oldpassword", "newpassword", "status_code"),
       [('xyzax', 'xxxx', 400),
         ('abc123', 'yuxz12', 200)
       ])
    def test_change_password(self, client, oldpassword, newpassword, status_code, account_pwd):
        (userid, access_token, refresh_token) = account_pwd

        headers = {"Authorization": f"Bearer {access_token}"}
        data = {'oldpassword': oldpassword, 'newpassword': newpassword}

        res = client.post("/api/auth/password",
                headers=headers,
                data=json.dumps(data),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == status_code, f"response code: {res.status_code}, message: {d}"
        if status_code != 200:
            assert d.error == 'PasswordFailure', f"message: {d}"
            assert d.failure_reason == 'ChangePasswordFailed', f"message: {d}"

    @pytest.fixture()
    def account_phone(self, client):
        account = {'username': 'login_by_phone test name1', 'auth_type': 'PHONE',
                    'phone': '+14089001234'}
        res = client.post('/api/auth/register',
                data=json.dumps(account),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"
        yield

    @pytest.mark.parametrize(("test_phone", "mock_token", "mock_token_recv", "status_code"),
       [('+14089001234', '123456', '000000', 400),
         ('+14089001234', '123456', '123456', 200)
       ])
    def test_login_by_phone(self, client, test_phone, mock_token, mock_token_recv, status_code, account_phone, mocker):
        data = {'phone': test_phone, 'auth_type': 'PHONE'}

        config = flask.current_app.config
        mocker.patch(__name__ + ".SMSFactory.create_instance", return_value=SimulatorClient(db, config))
        mocker.patch(__name__ + ".OTPGenerator.generate_otp", return_value=mock_token)

        # login and send sms
        res = client.post("/api/auth/login",
                data=json.dumps(data),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"

        # verify sms
        data = {"phone": test_phone, "token": mock_token_recv, "userid": d.userid}
        res = client.post("/api/auth/verify_sms",
                data=json.dumps(data),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == status_code, f"response code: {res.status_code}, message: {d}"
