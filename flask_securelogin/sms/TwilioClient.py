from twilio.rest import Client
from flask_securelogin.sms.SMSCall import SMSCall


class TwilioClient(SMSCall):
    def __init__(self, db, config):
        client = Client(config['TWILIO_ACCOUNT_SID'], config['TWILIO_AUTH_TOKEN'])
        verify = client.verify.services(config['TWILIO_SMS_SID'])

        self.db = db
        self.client = client
        self.verify = verify
        self.errors = None

    def send_sms(self, phone):
        self.verify.verifications.create(to=phone, channel='sms')

        return True

    def verify_sms(self, phone, token):
        self.errors = None
        result = self.verify.verification_checks.create(to=phone, code=token)

        return result.status == 'approved'

    def get_errors(self):
        return self.errors
