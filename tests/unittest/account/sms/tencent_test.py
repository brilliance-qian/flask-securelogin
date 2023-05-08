import pytest
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, ANY

from flask_securelogin.sms.TencentAPIClient import TencentAPIClient
from flask_securelogin.sms.OTPGenerator import OTPGenerator
from flask_securelogin import secure_auth

from tests.app import test_app


class TestTencentAPIClient:
    def test_sms_n_verify(self, test_app, mocker):
        config = test_app.config

        phone = "+14081234567"
        token = "512432"
        client = TencentAPIClient(secure_auth.db, config)

        resp_str = json.dumps({"SendStatusSet": [{"SerialNo": "2f522ecf-d557-4c0e-b6dc-f4842060c5ad", "PhoneNumber": phone, "Fee": 1, "SessionContext": "", "Code": "Ok", "Message": "send success", "IsoCode": "US"}], "RequestId": "24528f1d-7e23-48ac-b91f-65e48d37c79b"})   # noqa: E501
        tencent_resp = json.loads(resp_str, object_hook=lambda d: SimpleNamespace(**d))

        m_otp = mocker.patch(__name__ + ".OTPGenerator.generate_otp", return_value=token)
        m_verify = mocker.patch(__name__ + ".OTPGenerator.verify_otp", return_value=True)
        m_api = mocker.patch(__name__ + ".TencentAPIClient.tencent_api_call", return_value=tencent_resp)

        ok = client.send_sms(phone)
        assert ok

        m_api.assert_called_once_with(phone, ANY)
        m_otp.assert_called_once_with(phone)

        ok = client.verify_sms(phone, token)
        assert ok

        m_verify.assert_called_once_with(phone, token)
