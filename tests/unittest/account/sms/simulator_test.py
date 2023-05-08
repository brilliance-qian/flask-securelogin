import pytest
from unittest.mock import Mock, patch

from flask_securelogin.sms.SMSFactory import SMSFactory
from flask_securelogin import secure_auth

from tests.app import test_app
from tests.mockups.sms.SimulatorClient import SimulatorClient


class TestSimulatorClient:
    @pytest.mark.parametrize(("test_phone"),
       [("+14088801"),
        ("+8613800918821")
       ],)
    def test_verify_sms(self, test_phone, test_app, mocker):
        config = test_app.config

        config['SIMULATOR_CODE'] = None

        mocker.patch(__name__ + ".SMSFactory.create_instance", return_value=SimulatorClient(secure_auth.db, config))
        sms = SMSFactory.create_instance(secure_auth.db, config, test_phone)
        ok = sms.send_sms(test_phone)
        assert ok
        assert config['SIMULATOR_CODE'] is not None

        token = config['SIMULATOR_CODE']

        ok = sms.verify_sms(test_phone, token)
        assert ok

        errors = sms.get_errors()
        assert errors is None
