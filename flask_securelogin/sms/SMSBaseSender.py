from abc import abstractmethod
from flask_securelogin.sms.SMSCall import SMSCall
from flask_securelogin.sms.OTPGenerator import OTPGenerator


class SMSBaseSender(SMSCall):
    def __init__(self, db, config):
        self.db = db
        self.errors = None
        self.otp_generator = OTPGenerator(db, config)
        self.ttl = config['OTP_EXPIRATION']

    @abstractmethod
    def vendor_send_otp(self, phone, token) -> bool:
        pass

    def send_sms(self, phone):
        self.errors = None

        try:
            g = self.otp_generator
            token = g.gen_persist_otp(phone)
        except Exception:
            self.errors = "Failed to persist OTP to db"
            return False

        return self.vendor_send_otp(phone, token)

    def verify_sms(self, phone, token):
        g = self.otp_generator
        return g.verify_otp(phone, token)

    def get_errors(self):
        return self.errors
