import pytest
import json
from types import SimpleNamespace
from tests.apitest.client import client   # noqa: F401 # pylint:disable=unused-importt


# The test class validates input parameters for all api requests
class TestInvalidRequests:

    # test cases without token
    @pytest.mark.parametrize(("request_url", "mock_data", "mock_resp"),
        # login api
        [("/api/auth/login",
           {"email1": "1@x.com", "password": "xyz", "auth_type": "PASSWORD"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/login",
          {"email": "1@x.com", "password1": "xyz", "auth_type": "PASSWORD"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/login",
          {"email": "1@x.com", "password": "xyz", "auth_type1": "PASSWORD"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/login",
          {"phone1": "+1340123", "auth_type": "PHONE"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/login",
          {"email": "1@x.com", "password": "xyz", "auth_type": "UNKNOWN"},
          '{"error": "LoginFailure", "message": "unsupported authentication method"}'),

         # register api
         ("/api/auth/register",
           {"auth_type": "UNKNOWN", "username": "abc", "email": "2@a.com", "password": "zzz"},
          '{"error": "AccountCreationFailure", "message": "unsupported authentication method"}'),
         ("/api/auth/register",
           {"auth_type1": "PASSWORD", "username": "abc", "email": "2@a.com", "password": "zzz"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/register",
           {"auth_type": "PASSWORD", "username1": "abc", "email": "2@a.com", "password": "zzz"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/register",
           {"auth_type": "PASSWORD", "username": "abc", "email1": "2@a.com", "password": "zzz"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/register",
           {"auth_type": "PASSWORD", "username": "abc", "email": "2@a.com", "password1": "zzz"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/register",
           {"auth_type": "PHONE", "username1": "abc", "phone": "+1340123013"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/register",
           {"auth_type": "PHONE", "username": "abc", "phone2": "+1340123013"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),

         # verify_sms
         ("/api/auth/verify_sms",
           {"userid1": "24121", "token": "123456", "phone": "+1340123013"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/verify_sms",
           {"userid": "24121", "token1": "123456", "phone": "+1340123013"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/verify_sms",
           {"userid": "24121", "token": "123456", "phone1": "+1340123013"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
        ],)
    def test_invalid_requests_wo_token(self, client, request_url, mock_data, mock_resp):
        res = client.post(request_url,
                data=json.dumps(mock_data),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        expected_resp = json.loads(mock_resp, object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == 400, f"response code: {res.status_code}, message: {d}"
        assert d.error == expected_resp.error, f"response code: {res.status_code}, message: {d}"
        # assert d.message == expected_resp.message, f"response code: {res.status_code}, message: {d}"

    @pytest.fixture()
    def account_w_tokens(self, client):
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

    # test cases without token
    @pytest.mark.parametrize(("request_url", "mock_data", "mock_resp"),
        # change password
        [("/api/auth/password",
           {"oldpassword1": "xyz", "newpassword": "abc"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
         ("/api/auth/password",
           {"oldpassword": "xyz", "newpassword1": "abc"},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),

         # logout
         ("/api/auth/logout",
           {'refresh_token1': 'xyz'},
          '{"error": "KeyError", "message": "Invalid input parameters"}'),
        ],)
    def test_invalid_requests_token(self, client, request_url,
               mock_data, mock_resp, account_w_tokens):
        (userid, access_token, refresh_token) = account_w_tokens

        headers = {"Authorization": f"Bearer {access_token}"}

        res = client.post(request_url,
                          headers=headers,
                          data=json.dumps(mock_data),
                          content_type='application/json')

        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        expected_resp = json.loads(mock_resp, object_hook=lambda d: SimpleNamespace(**d))

        assert res.status_code == 400, f"response code: {res.status_code}, message: {d}"
        assert d.error == expected_resp.error
        # assert d.message == expected_resp.message
