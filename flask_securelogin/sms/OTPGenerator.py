from flask_securelogin.sms.models import AuthOTP

import math
import random
import time


class OTPGenerator():
    def __init__(self, db, config):
        self._config = config
        self._db = db
        self._expiration = config['OTP_EXPIRATION']
        self._num_digits = config['OTP_DIGITS']

    def update_token_to_db(self, phone, token):
        otp = AuthOTP.query.filter_by(alias=phone).first()
        if otp is None:
            otp = AuthOTP()
            otp.alias = phone
            otp.created_ts = int(time.time())
            otp.sms = token

            self._db.session.add(otp)
        else:
            otp.created_ts = int(time.time())
            otp.sms = token

        self._db.session.commit()

        return token

    def get_token_from_db(self, phone):
        otp = AuthOTP.query.filter_by(alias=phone).first()
        if otp is None:
            return (None, None)

        return (otp.sms, otp.created_ts)

    def generate_otp(self, phone):
        digits = "0123456789"
        otp = ''
        for i in range(self._num_digits):
            otp += digits[math.floor(random.random() * 10)]

        return otp

    def gen_persist_otp(self, phone):
        otp = self.generate_otp(phone)
        self.update_token_to_db(phone, otp)
        return otp

    def verify_otp(self, phone, token):
        (otp, created_ts) = self.get_token_from_db(phone)
        if otp is None or created_ts is None:
            return False

        if (time.time() - created_ts) > self._expiration * 60:
            return False

        return otp == token
