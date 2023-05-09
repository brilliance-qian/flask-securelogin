import pytest
import json
import time_machine
import datetime as dt
from datetime import timedelta

import flask
from types import SimpleNamespace
from unittest.mock import Mock, patch  # noqa: F401 # pylint:disable=unused-import

from tests.app import db
from flask_securelogin.sms.SMSFactory import SMSFactory  # noqa: F401 # pylint:disable=unused-import
from flask_securelogin.sms.OTPGenerator import OTPGenerator  # noqa: F401 # pylint:disable=unused-import
from flask_securelogin.models import User

from tests.apitest.client import client  # noqa: F401 # pylint:disable=unused-import
from tests.mockups.sms.SimulatorClient import SimulatorClient

from flask_jwt_extended import decode_token


class TestToken:
    @pytest.fixture()
    def reg_tokens(self, client):
        email = 'abc1@logintest.com'
        password = 'abc123'
        account = {'username': 'login test name1', 'auth_type': 'PASSWORD',
                    'email': email, 'password': password}
        res = client.post('/api/auth/register',
                data=json.dumps(account),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"

        userid = d.userid
        access_token = d.access_token
        refresh_token = d.refresh_token
        return (userid, access_token, refresh_token)

    @pytest.fixture()
    def login_by_phone_tokens(self, client, mocker):
        return self.login_by_phone_tokens_common(client, mocker)

    @pytest.fixture()
    def login_by_phone_tokens_dup(self, client, mocker):
        return self.login_by_phone_tokens_common(client, mocker)

    def login_by_phone_tokens_common(self, client, mocker):
        phone = "+14089001234"
        # mock user record
        mock_user = User(username='login_by_phone test name1',
                 phone=phone, status='active', auth_type='PHONE')
        db.session.add(mock_user)
        db.session.commit()

        # mock SMS sender
        config = flask.current_app.config
        mocker.patch(__name__ + ".SMSFactory.create_instance", return_value=SimulatorClient(db, config))

        # login and send sms
        data = {'phone': phone, 'auth_type': 'PHONE'}

        res = client.post("/api/auth/login",
                data=json.dumps(data),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"

        token_recv = config['SIMULATOR_CODE']

        # verify sms
        data = {"phone": phone, "token": token_recv, "userid": d.userid}
        res = client.post("/api/auth/verify_sms",
                data=json.dumps(data),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"

        userid = d.userid
        access_token = d.access_token
        refresh_token = d.refresh_token
        return (userid, access_token, refresh_token)

    @pytest.fixture()
    def login_by_pwd_tokens(self, client, mocker):
        return self.login_by_pwd_tokens_common(client, mocker)

    @pytest.fixture()
    def login_by_pwd_tokens_dup(self, client, mocker):
        return self.login_by_pwd_tokens_common(client, mocker)

    def login_by_pwd_tokens_common(self, client, mocker):
        email = 't1@mytest.com'
        password = "duzzy"
        mock_user = User(email=email, status='active', auth_type='PASSWORD')

        if mock_user is not None:
            mock_user.set_password(password)    # ensure password check is always correct

        db.session.add(mock_user)
        db.session.commit()

        data = {'email': email, 'password': password, 'auth_type': 'PASSWORD'}
        res = client.post("/api/auth/login",
                data=json.dumps(data),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"

        userid = d.userid
        access_token = d.access_token
        refresh_token = d.refresh_token
        return (userid, access_token, refresh_token)

    def get_op_resp(self, op, client, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}

        url = "/api/auth/" + op
        res = client.post(url,
                headers=headers,
                data=json.dumps({}),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        return (res.status_code, d)

    def get_refresh_resp(self, client, refresh_token):
        headers = {"Authorization": f"Bearer {refresh_token}"}

        res = client.post("/api/auth/refresh",
                headers=headers,
                data=json.dumps({}),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        return (res.status_code, d)

    def get_logout_resp(self, client, access_token, refresh_token):
        headers = {"Authorization": f"Bearer {access_token}"}

        res = client.post("/api/auth/logout",
                headers=headers,
                data=json.dumps({'refresh_token': refresh_token}),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        return (res.status_code, d)

    def get_logout_all_others_resp(self, client, access_token, refresh_token):
        headers = {"Authorization": f"Bearer {access_token}"}

        res = client.post("/api/auth/logout_all_other_sessions",
                headers=headers,
                data=json.dumps({'refresh_token': refresh_token}),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        return (res.status_code, d)

    # happy path testing: account register or login, op, logout
    @pytest.mark.parametrize(("get_tokens"),
       [("reg_tokens"), ("login_by_pwd_tokens"), ("login_by_phone_tokens")
      ])
    def test_login_tokens(self, client, get_tokens, request):
        (userid, access_token, refresh_token) = request.getfixturevalue(get_tokens)

        # the operation should be authorized
        status_code, d = self.get_op_resp("op", client, access_token)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

        # the logout should succeed
        status_code, d = self.get_logout_resp(client, access_token, refresh_token)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

        # the logout should fail if it continues to logout with the same refresh_token
        status_code, d = self.get_logout_resp(client, access_token, refresh_token)
        assert status_code == 400, f"response code: {status_code}, message: {d}"
        assert d.error == 'LoginFailure' and d.failure_reason == 'AccountInactiveToken'

    @pytest.mark.parametrize(("get_tokens"),
       [("reg_tokens"), ("login_by_pwd_tokens"), ("login_by_phone_tokens")
      ])
    def test_fresh_tokens(self, client, get_tokens, request, mocker):
        # set token expiration to 10 minutes
        config = flask.current_app.config
        config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)

        (userid, access_token, refresh_token) = request.getfixturevalue(get_tokens)

        # access token is fresh, it succeed
        status_code, d = self.get_op_resp("op2", client, access_token)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

        # now, let's refresh the access token
        status_code, d = self.get_refresh_resp(client, refresh_token)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

        # get the new tokens
        access_token = d.access_token
        refresh_token = d.refresh_token

        # access token freshness expired, it should fail
        status_code, d = self.get_op_resp("op2", client, access_token)
        assert status_code == 401, f"response code: {status_code}, message: {d}"
        assert d.error == 'FreshTokenRequired'

    @pytest.mark.parametrize(("get_tokens"),
       [("reg_tokens"), ("login_by_pwd_tokens"), ("login_by_phone_tokens")
      ])
    def test_login_expired_tokens(self, client, get_tokens, request, mocker):
        # set token expiration to 10 minutes
        config = flask.current_app.config
        config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)

        # mock up the tokens are created 30 minutes ago
        mock_dt = dt.datetime.utcnow() - timedelta(minutes=30)
        traveller = time_machine.travel(mock_dt)
        traveller.start()
        (userid, access_token, refresh_token) = request.getfixturevalue(get_tokens)
        traveller.stop()

        # access token expired, it should fail
        status_code, d = self.get_op_resp("op", client, access_token)
        assert status_code == 401, f"response code: {status_code}, message: {d}"
        assert d.error == 'AccessTokenExpired'

        # now, let's refresh the access token
        status_code, d = self.get_refresh_resp(client, refresh_token)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

        # get the new tokens
        access_token = d.access_token
        refresh_token = d.refresh_token

        # try with the new access token, it should succeed
        status_code, d = self.get_op_resp("op", client, access_token)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

    @pytest.mark.parametrize(("get_tokens"),
       [("reg_tokens"), ("login_by_pwd_tokens"), ("login_by_phone_tokens")
      ])
    def test_expired_refresh_token(self, client, get_tokens, request, mocker):
        # set access token expiration to 10 minutes
        # set refresh token expiration to 30 days
        config = flask.current_app.config
        config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)
        config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

        # mock up the tokens are created 31 days ago
        mock_dt = dt.datetime.utcnow() - timedelta(days=31)
        traveller = time_machine.travel(mock_dt)
        traveller.start()
        (userid, access_token, refresh_token) = request.getfixturevalue(get_tokens)

        # the operation should be authorized
        status_code, d = self.get_refresh_resp(client, refresh_token)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

        # restore time machine
        traveller.stop()

        # refresh_token expired, it should fail
        status_code, d = self.get_refresh_resp(client, refresh_token)
        assert status_code == 401, f"response code: {status_code}, message: {d}"
        assert d.error == 'RefreshTokenExpired'

    @pytest.mark.parametrize(("logout_type"),
       [("logout"), ("logout_all_other_sessions")
      ])
    @pytest.mark.parametrize(("get_tokens", "get_tokens_dup"),
       [("login_by_phone_tokens", "login_by_phone_tokens_dup"),
#         ("login_by_pwd_tokens", "login_by_pwd_tokens_dup")
      ])
    def test_concurrent_sessions(self, client, get_tokens, get_tokens_dup, logout_type, request, mocker):
        # set access token expiration to 10 minutes
        # set refresh token expiration to 30 days
        config = flask.current_app.config
        config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)
        config['JWT_FRESH_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=5)

        config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

        # two sessions
        (userid1, access_token1, refresh_token1) = request.getfixturevalue(get_tokens)
        (userid2, access_token2, refresh_token2) = request.getfixturevalue(get_tokens_dup)

        # validate they are two sessions
        jwt1 = decode_token(refresh_token1)
        jwt2 = decode_token(refresh_token2)
        assert jwt1['sid'] != jwt2['sid']
        assert jwt1['jti'] != jwt2['jti']

        # op are functional on both sessions
        status_code, d = self.get_op_resp("op", client, access_token1)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

        status_code, d = self.get_op_resp("op", client, access_token2)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

        if logout_type == "logout_all_other_sessions":
            # logout all out sessions
            status_code, d = self.get_logout_all_others_resp(client, access_token2, refresh_token2)
            assert status_code == 200, f"response code: {status_code}, message: {d}"
        else:
            # refresh token are functional on both sessions
            status_code, d1 = self.get_refresh_resp(client, refresh_token1)
            assert status_code == 200, f"response code: {status_code}, message: {d1}"
            access_token1 = d1.access_token
            refresh_token1 = d1.refresh_token

            status_code, d2 = self.get_refresh_resp(client, refresh_token2)
            assert status_code == 200, f"response code: {status_code}, message: {d2}"
            access_token2 = d2.access_token
            refresh_token2 = d2.refresh_token

            # logout session1
            status_code, d = self.get_logout_resp(client, access_token1, refresh_token1)
            assert status_code == 200, f"response code: {status_code}, message: {d}"

        # using the refresh_token1 will be refused
        status_code, d = self.get_refresh_resp(client, refresh_token1)
        assert status_code == 401, f"response code: {status_code}, message: {d}"

        # refresh token continues functional on session2
        status_code, d2 = self.get_refresh_resp(client, refresh_token2)
        assert status_code == 200, f"response code: {status_code}, message: {d2}"
        access_token2 = d2.access_token
        refresh_token2 = d2.refresh_token

    @pytest.mark.parametrize(("get_tokens"),
       [("reg_tokens"), ("login_by_pwd_tokens"), ("login_by_phone_tokens")]
    )
    def test_freshness_logout_all_other_sessions(self, client, get_tokens, request, mocker):
        # set token expiration to 10 minutes
        (userid, access_token, refresh_token) = request.getfixturevalue(get_tokens)

        # access token is fresh, it succeed
        status_code, d = self.get_logout_all_others_resp(client, access_token, refresh_token)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

    @pytest.mark.parametrize(("get_tokens"),
       [("reg_tokens"), ("login_by_pwd_tokens"), ("login_by_phone_tokens")]
    )
    def test_non_freshness_logout_all_other_sessions(self, client, get_tokens, request, mocker):
        # set token expiration to 10 minutes
        (userid, access_token, refresh_token) = request.getfixturevalue(get_tokens)

        # refresh the tokens
        status_code, d = self.get_refresh_resp(client, refresh_token)
        assert status_code == 200, f"response code: {status_code}, message: {d}"
        access_token = d.access_token
        refresh_token = d.refresh_token

        # access token is not fresh, it should fail
        status_code, d = self.get_logout_all_others_resp(client, access_token, refresh_token)
        assert status_code == 401, f"response code: {status_code}, message: {d}"
