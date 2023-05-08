import pytest
import time
from flask_securelogin.sms.OTPGenerator import OTPGenerator
from flask_securelogin import secure_auth

from tests.app import test_app


class TestOTPGenerator:
    def test_token_generator(self, test_app):
        config = test_app.config
        num_digits = config['OTP_DIGITS']

        phone = "+1231023"
        g = OTPGenerator(secure_auth.db, config)

        # examine otp digit length
        token = g.gen_persist_otp(phone)
        assert len(token) == num_digits
        assert token.isdigit()

        ok = g.verify_otp(phone, token)
        assert ok

    @pytest.mark.parametrize(("expiration", "duration", "status"),
       [(60, 70, False),
        (60, 60, False),
        (60, 50, True)
       ],)
    def test_token_expiration(self, expiration, duration, status, test_app, mocker):
        config = test_app.config

        config['OTP_EXPIRATION'] = expiration
        ts = time.time() - duration * 60

        phone = "+1231023"
        token = "412312"
        g = OTPGenerator(secure_auth.db, config)

        # mock the expiration time
        m = mocker.patch(__name__ + ".OTPGenerator.get_token_from_db", return_value=(token, ts))
        ok = g.verify_otp(phone, token)

        assert ok == status
        m.assert_called_once_with(phone)
