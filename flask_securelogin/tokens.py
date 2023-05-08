from flask_securelogin.exception import AppException
from flask_securelogin.models import UserActiveToken

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

import uuid


class TokenManager():
    def __init__(self, db):
        self._db = db

    def start_new_session(self, userid):
        # internal session id
        sid = str(uuid.uuid4())

        (access_token, refresh_token) = self.create_tokens(userid, sid, True)
        self.insert_refresh_token_in_db(userid, refresh_token)

        return (access_token, refresh_token)

    def create_tokens(self, userid, sid, fresh):
        # create access_token and refresh_token
        access_token = create_access_token(identity=userid, fresh=fresh)
        refresh_token = create_refresh_token(identity=userid, additional_claims={"sid": sid})

        # update it to database
        return (access_token, refresh_token)

    def insert_refresh_token_in_db(self, userid, refresh_token):
        # decode refresh token
        new_jwt = decode_token(refresh_token)

        # create new record for UserActiveToken
        active_token = UserActiveToken(userid=userid)

        active_token.sessionid = new_jwt['sid']
        active_token.jti = new_jwt['jti']
        active_token.created_at = new_jwt['iat']
        active_token.expired_at = new_jwt['exp']
        active_token.active = True

        # insert to DB
        self._db.session.add(active_token)
        self._db.session.commit()

        return

    def update_refresh_token_in_db(self, active_token, refresh_token):
        # decode refresh token
        new_jwt = decode_token(refresh_token)

        # update the fields
        active_token.jti = new_jwt['jti']
        active_token.created_at = new_jwt['iat']
        active_token.expired_at = new_jwt['exp']
        active_token.active = True

        # update it to DB
        self._db.session.commit()

        return

    def refresh_token_sanity_check(self, active_token, jti, userid):

        if active_token is None:
            raise AppException("LoginFailure", "AccountNoLogin", "The user didn't login")

        if active_token.jti != jti:
            raise AppException("LoginFailure", "AccountObsoleteToken", "The refresh token is already obsolete")

        if active_token.userid != userid:
            raise AppException("LoginFailure", "AccountInvalidSession", "Corrupted refresh_token, userid doesn't match")

        if not active_token.active:
            raise AppException("LoginFailure", "AccountInactiveToken",
                               "The refresh token is inactive, user already logout")

        return

    def refresh_tokens(self, refresh_token_jwt):
        userid = refresh_token_jwt['sub']
        jti = refresh_token_jwt['jti']
        sid = refresh_token_jwt['sid']

        # validate whether the refresh_token is consistent with the active token for the user
        active_token = UserActiveToken.query.filter_by(sessionid=sid).first()

        self.refresh_token_sanity_check(active_token, jti, userid)

        # create new tokens
        (access_token, refresh_token) = self.create_tokens(userid, sid, False)

        # update it it the DB
        self.update_refresh_token_in_db(active_token, refresh_token)

        return (access_token, refresh_token)

    def logout_token(self, refresh_token, access_token_jwt):
        # decode refresh_token
        refresh_token_jwt = decode_token(refresh_token)

        userid = refresh_token_jwt['sub']
        jti = refresh_token_jwt['jti']
        sid = refresh_token_jwt['sid']

        if access_token_jwt is not None and access_token_jwt['sub'] != userid:
            raise AppException("AccountLogoutFailure", "InvalidUserId",
                               "The refresh token is inconsistent with access_token.")

        # validate whether the refresh_token is consistent with the active token for the user
        active_token = UserActiveToken.query.filter_by(sessionid=sid).first()
        self.refresh_token_sanity_check(active_token, jti, userid)

        active_token.active = False
        self._db.session.commit()

    def check_if_token_revoked(self, token_jwt):
        token_type = token_jwt['type']
        if token_type != 'refresh':
            # access token, skip check
            # future: check the token against cache
            return False

        jti = token_jwt['jti']
        sid = token_jwt['sid']

        active_token = UserActiveToken.query.filter_by(sessionid=sid).first()
        if active_token is None:
            return True

        if active_token.jti != jti:
            return True

        return not active_token.active

    def logout_all_other_sessions(self, access_token_jwt, refresh_token):
        # decode refresh_token
        refresh_token_jwt = decode_token(refresh_token)

        userid = refresh_token_jwt['sub']
        sid = refresh_token_jwt['sid']

        if access_token_jwt['sub'] != userid:
            raise AppException("KickoutAllSessionFailure", "InvalidUserId",
                               "The refresh token is inconsistent with access_token.")

        user_sessions = UserActiveToken.query.filter_by(userid=userid).all()

        for active_token in user_sessions:
            if active_token.sessionid == sid:
                continue

            if not active_token.active:
                continue

            active_token.active = False

        self._db.session.commit()

        return
