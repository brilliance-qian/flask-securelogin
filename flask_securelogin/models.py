from werkzeug.security import generate_password_hash, check_password_hash
from flask_securelogin import secure_auth

db = secure_auth.db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(36), index=True, unique=True)

    username = db.Column(db.String(50), index=True)
    auth_type = db.Column(db.String(10))
    email = db.Column(db.String(120), index=True)
    phone = db.Column(db.String(20), index=True)
    password_hash = db.Column(db.String(128))

    status = db.Column(db.String(10))
    time_created = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# The current active refresh_token for a member. The table should be updated
# when every refresh_token is refreshed and set to false when a user logout
class UserActiveToken(db.Model):
    __tablename__ = 'active_tokens'

    # internal id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # internal session id
    sessionid = db.Column(db.String(36), index=True, unique=True)

    # the user id linked to User table
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    # refresh token
    jti = db.Column(db.String(36), nullable=False, index=True)

    # set to FALSE when a user log out
    active = db.Column(db.Boolean, unique=False, default=True)

    # indicate when the jti was created
    created_at = db.Column(db.Integer, nullable=False)

    # indicate the token expiration time, used to purge the DB
    # for rows that token is expired
    expired_at = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<UserActiveToken {}>'.format(self.sessionid)
