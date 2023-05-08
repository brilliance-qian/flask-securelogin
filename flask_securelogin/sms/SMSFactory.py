from flask_securelogin.sms.TwilioClient import TwilioClient
from flask_securelogin.sms.UniSMSClient import UniSMSClient
from flask_securelogin.sms.TencentAPIClient import TencentAPIClient


class SMSFactory():
    def get_vendor(config, phone):
        vendor = config['SMS_VENDOR']       # default setting

        # SMS vendor routing
        if 'TWILIO_TESTING_PHONES' in config and phone in config['TWILIO_TESTING_PHONES']:
            vendor = 'twillio'
        elif phone.find('+86') == 0: 		# china phone number
            vendor = 'uni-sms'
        elif phone.find('+1') == 0:			# US phone number
            vendor = 'tencent'

        return vendor.lower()

    def create_instance(db, config, phone):
        vendor = SMSFactory.get_vendor(config, phone)

        if vendor == 'twillio':
            return TwilioClient(db, config)
        elif vendor == 'uni-sms':
            return UniSMSClient(db, config)
        elif vendor == 'tencent':
            return TencentAPIClient(db, config)

        return None
