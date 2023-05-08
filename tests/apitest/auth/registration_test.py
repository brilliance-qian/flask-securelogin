import pytest
import json
from tests.apitest.client import client  # noqa: F401 # pylint:disable=unused-import


class TestRegistration:
    @pytest.mark.parametrize(
        ("account_to_create", "must_fields", "none_fields"),
        [
          # register by password
          ({'username': 'reg_success name1', 'auth_type': 'PASSWORD',
             'email': 'abc1@test.com', 'password': 'abc123'},
            ['userid', 'message', 'access_token', 'refresh_token'], []),

          # register by phone
          ({'username': 'reg_success name2', 'auth_type': 'PHONE', 'phone': '+14089980121'},
            ['userid', 'message'], ['access_token', 'refresh_token'])
        ])
    def test_register_success(self, client, account_to_create, must_fields, none_fields):
        res = client.post('/api/auth/register',
                data=json.dumps(account_to_create),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"

        for f in must_fields:
            assert d[f] is not None, f"return message: {d}"
        for f in none_fields:
            assert f not in d, f"return message: {d}"

    @pytest.mark.parametrize(
        ("existing_account", "dup_account", "status_code"),
        [
          # register by password
          # duplicate username is allowed
          ({'username': 'reg_fail name1', 'auth_type': 'PASSWORD',
             'email': 'reg_fail1@test.com', 'password': 'abc123'},
           {'username': 'reg_fail name1', 'auth_type': 'PASSWORD',
             'email': 'reg_fail_xyz@test.com', 'password': 'xyz123'}, 200),
          # duplicate phone is not allowed
          ({'username': 'reg_fail name2', 'auth_type': 'PASSWORD',
             'email': 'reg_fail_abc@test.com', 'password': 'abc123'},
           {'username': 'reg_fail name21', 'auth_type': 'PASSWORD',
             'email': 'reg_fail_abc@test.com', 'password': 'xyz123'}, 400),

          # register by phone
          # duplicate username is allowed
          ({'username': 'phone reg name2', 'auth_type': 'PHONE', 'phone': '+14089981121'},
           {'username': 'phone reg name2', 'auth_type': 'PHONE', 'phone': '+14089981122'},
           200),
          # duplicate phone is not allowed
          ({'username': 'phone reg name3', 'auth_type': 'PHONE', 'phone': '+14089982121'},
           {'username': 'phone reg name31', 'auth_type': 'PHONE', 'phone': '+14089982121'},
            400)
        ])
    def test_register_fail_dup_account(self, client, existing_account, dup_account, status_code):
        res = client.post('/api/auth/register',
                data=json.dumps(existing_account),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"

        res = client.post('/api/auth/register',
                data=json.dumps(dup_account),
                content_type='application/json')
        assert res.status_code == status_code, f"response code: {res.status_code}, message: {d}"
