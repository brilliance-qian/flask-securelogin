from flask_securelogin.sms.SMSBaseSender import SMSBaseSender
import requests
import json


class UniSMSClient(SMSBaseSender):
    def __init__(self, db, config):
        super().__init__(db, config)
        self.accessKeyId = config['UNISMS_ACCESSKEY_ID']
        self.signature = config['UNISMS_SIGNATURE']

    def umisms_api_call(self, phone, token):
        url = "https://uni.apistd.com/?action=sms.message.send&accessKeyId=" + self.accessKeyId

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "to": phone,
            "signature": self.signature,
            "templateId": "pub_verif_login",
            "templateData": {"code": token, "ttl": self.ttl}
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.text

    def vendor_send_otp(self, phone, token):
        # send token through Uni-SMS api
        resp = self.umisms_api_call(phone, token)

        # parse the response
        x = json.loads(resp)
        code = x['code']
        message = x['message']

        if int(code) != 0:
            self.errors = "Failed to send SMS uni-sms due to " + message + ", error code: " + code
            return False

        return True
