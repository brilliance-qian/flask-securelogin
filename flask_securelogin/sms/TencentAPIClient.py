from flask_securelogin.sms.SMSBaseSender import SMSBaseSender

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models


class TencentAPIClient(SMSBaseSender):
    def __init__(self, db, config):
        super().__init__(db, config)
        self.secretId = config['TENCENT_SECRET_ID']
        self.secretKey = config['TENCENT_SECRET_KEY']
        self.sdkAppId = config['TENCENT_SDK_APPID']
        self.templateId = config['TENCENT_TEMPLATE_ID']
        self.senderId = config['TENCENT_SENDER_ID']
        self.appName = config['TENCENT_APP_NAME']

    def tencent_api_call(self, phone, token):
        # the secretId and secretKey can be acquired the tencent website
        # from https://console.cloud.tencent.com/cam/capi
        # they are configured in the application previously
        cred = credential.Credential(self.secretId, self.secretKey)

        # initiate http profile
        httpProfile = HttpProfile()
        httpProfile.endpoint = "sms.tencentcloudapi.com"

        # initiate an instance of http client
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        client = sms_client.SmsClient(cred, "ap-guangzhou", clientProfile)

        # initiate a request
        req = models.SendSmsRequest()
        params = {
            "PhoneNumberSet": [phone],
            "SmsSdkAppId": self.sdkAppId,
            "TemplateId": self.templateId,
            "TemplateParamSet": [self.appName, token, str(self.ttl)],
            "SenderId": self.senderId
        }
        req.from_json_string(json.dumps(params))

        # send the request to Tencent cloud
        resp = client.SendSms(req)

        # parse the response
        # x = resp.to_json_string()

        return resp

    def vendor_send_otp(self, phone, token):
        # send token through Tencent api
        try:
            resp = self.tencent_api_call(phone, token)

            stat = resp.SendStatusSet[0]
            if stat.Code != 'Ok':
                self.errors = stat.Code + ": " + stat.Message
                return False
        except TencentCloudSDKException as err:
            self.errors = err.code + ": " + err.message
            return False

        return True
