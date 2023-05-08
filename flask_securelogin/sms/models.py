from flask_securelogin import secure_auth

db = secure_auth.db


class AuthOTP(db.Model):
    alias = db.Column(db.String(120), primary_key=True)
    sms = db.Column(db.String(10))
    created_ts = db.Column(db.BigInteger)
