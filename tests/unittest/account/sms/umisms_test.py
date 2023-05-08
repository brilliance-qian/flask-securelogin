import pytest
import json
import requests
from types import SimpleNamespace
from unittest.mock import MagicMock, ANY

from flask_securelogin.sms.UniSMSClient import UniSMSClient
from flask_securelogin.sms.OTPGenerator import OTPGenerator
from flask_securelogin import secure_auth

from tests.app import test_app


class TestUniSMSClient:
    def test_sms_n_verify(self, test_app, mocker):
        config = test_app.config

        phone = "+14081234567"
        token = "512432"
        client = UniSMSClient(secure_auth.db, config)

        resp_mock = '{"data":{"currency":"CNY","recipients":1,"messageCount":1,"totalAmount":"0.100000","payAmount":"0.100000","virtualAmount":"0","messages":[{"id":"528eaac6a185eb5d3ec9536312915461","to":"' + phone + '","regionCode":"US","countryCode":"1","messageCount":1,"status":"sent","upstream":"emay.intl.standard","price":"0.100000"}]},"code":"0","message":"Success"}'  # noqa: E501

        m_otp = mocker.patch(__name__ + ".OTPGenerator.generate_otp", return_value=token)
        m_verify = mocker.patch(__name__ + ".OTPGenerator.verify_otp", return_value=True)
        m_api = mocker.patch(__name__ + ".UniSMSClient.umisms_api_call", return_value=resp_mock)

        ok = client.send_sms(phone)
        assert ok

        m_api.assert_called_once_with(phone, ANY)
        m_otp.assert_called_once_with(phone)

        ok = client.verify_sms(phone, token)
        assert ok

        m_verify.assert_called_once_with(phone, token)

    def test_request_data(self, test_app, mocker):
        config = test_app.config

        phone = "+14081234567"
        token = "512432"

        url = "https://uni.apistd.com/?action=sms.message.send&accessKeyId=" + config['UNISMS_ACCESSKEY_ID']
        headers = {"Content-Type": "application/json"}
        data = {
            "to": phone,
            "signature": config['UNISMS_SIGNATURE'],
            "templateId": "pub_verif_login",
            "templateData": {"code": token, "ttl": config['OTP_EXPIRATION']}
        }
        payload = json.dumps(data)

        mock_resp = "Success"
        mock_requests = mocker.patch("requests.post")
        mock_requests.return_value.text = mock_resp

        client = UniSMSClient(secure_auth.db, config)
        resp = client.umisms_api_call(phone, token)
        assert resp == mock_resp
        mock_requests.assert_called_with(url, headers=headers, data=payload)
