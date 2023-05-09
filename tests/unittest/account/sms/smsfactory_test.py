import pytest

from flask_securelogin.sms.SMSFactory import SMSFactory
from flask_securelogin import secure_auth

from tests.app import test_app


class TestSMSFactory:
    @pytest.mark.parametrize(("test_phone", "class_name"),
       [("+18091234567", "TencentAPIClient"),
        ("+14089057799", "TwilioClient"),
        ("+4180890599", "TwilioClient"),
        ("+8613605439004", "UniSMSClient")
       ],)
    def test_vendor(self, test_phone, class_name, test_app):
        config = test_app.config
        config['TWILIO_TESTING_PHONES'] = ('+14089057799')

        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        sms = SMSFactory.create_default_service(secure_auth.db, config, test_phone)
        assert sms.__class__.__name__ == class_name
