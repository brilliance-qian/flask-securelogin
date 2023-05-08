from flask_securelogin.sms.SMSBaseSender import SMSBaseSender


class SimulatorClient(SMSBaseSender):
    def __init__(self, db, config):
        super().__init__(db, config)
        self.config = config

    def vendor_send_otp(self, phone, token):
        self.config['SIMULATOR_CODE'] = token
        return True
