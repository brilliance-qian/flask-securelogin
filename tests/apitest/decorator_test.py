import pytest
import json
import flask
from types import SimpleNamespace

from tests.apitest.client import client  # noqa: F401 # pylint:disable=unused-import
from flask_securelogin import secure_auth
from flask_securelogin.models import User
from flask_jwt_extended import decode_token

from tests.app import db
from tests.mockups.sms.SimulatorClient import SimulatorClient

# map for testing check_if_access_token_revoked
active_tokens = {}


class TestDecorators:
    @secure_auth.create_sms_service
    def create_sms_service_instance(db, config, phone):
        return SimulatorClient(db, config)

    @secure_auth.check_if_access_token_revoked
    def check_if_access_token_revoked(jti):
        if jti in active_tokens:
            return active_tokens[jti]

        return False

    def get_op_resp(self, op, client, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}

        url = "/api/auth/" + op
        res = client.post(url,
                headers=headers,
                data=json.dumps({}),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        return (res.status_code, d)

    def test_decorators(self, client):
        phone = "+14089797934"

        # mock user record
        mock_user = User(username='login_by_phone test name1',
                 phone=phone, status='active', auth_type='PHONE')
        db.session.add(mock_user)
        db.session.commit()

        ##############################################################
        # Test create_sms_service by verify sms from SimulatorClient
        ##############################################################

        # login and send sms
        data = {'phone': phone, 'auth_type': 'PHONE'}

        res = client.post("/api/auth/login",
                data=json.dumps(data),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"

        config = flask.current_app.config
        token_recv = config['SIMULATOR_CODE']

        # verify sms
        data = {"phone": phone, "token": token_recv, "userid": d.userid}
        res = client.post("/api/auth/verify_sms",
                data=json.dumps(data),
                content_type='application/json')
        d = json.loads(res.data.decode('utf-8'), object_hook=lambda d: SimpleNamespace(**d))
        assert res.status_code == 200, f"response code: {res.status_code}, message: {d}"
        access_token = d.access_token

        ##############################################################
        # Test check_if_access_token_revoked
        ##############################################################
        jwt = decode_token(access_token)
        jti = jwt['jti']

        # access token is not revoked
        active_tokens[jti] = False
        status_code, d = self.get_op_resp("op", client, access_token)
        assert status_code == 200, f"response code: {status_code}, message: {d}"

        # access token is revoked
        active_tokens[jti] = True
        status_code, d = self.get_op_resp("op", client, access_token)
        assert status_code == 401, f"response code: {status_code}, message: {d}"
        assert d.msg == 'Token has been revoked', f"response code: {status_code}, message: {d}"
