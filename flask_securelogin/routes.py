import flask
import logging
from flask_securelogin.exception import AppException
from flask_securelogin.errors import bad_request, error_response
from flask_securelogin.account import AccountManager
from flask_securelogin.tokens import TokenManager

from sqlalchemy import exc
from flask import request

from flask_jwt_extended import (
    get_jwt,
    jwt_required,
    get_jwt_identity
)

from flask_securelogin import secure_auth

bp = secure_auth.bp
jwt = secure_auth.jwt

log = logging.getLogger(__name__)


@bp.route('/auth/register', methods=['POST'])
def register():
    config = flask.current_app.config
    d = request.get_json()

    auth_type = d['auth_type']
    if auth_type not in ['PASSWORD', 'PHONE', 'APPLE_ID', 'GOOGLE_ID']:
        return bad_request("AccountCreationFailure", "unsupported authentication method")

    account_manager = AccountManager(secure_auth.db, config)
    new_user = None

    if auth_type == 'PASSWORD':
        username = d['username']
        email = d['email']
        password = d['password']

        new_user = account_manager.create_user_w_password(username, email, password)
    elif auth_type == 'PHONE':
        username = d['username']
        phone = d['phone']

        new_user = account_manager.create_user_w_phone(username, phone)

    if new_user is None:
        return bad_request("AccountCreationFailure", "account creation method is not supported yet")

    resp = {'message': 'registered successfully', 'userid': new_user.public_id}
    if auth_type == 'PASSWORD':
        token_manager = TokenManager(secure_auth.db)
        (access_token, refresh_token) = token_manager.start_new_session(new_user.id)
        resp['access_token'] = access_token
        resp['refresh_token'] = refresh_token

    return resp


@bp.route('/auth/login', methods=['POST'])
@bp.route('/auth/login_sms', methods=['POST'])
def login():
    d = request.get_json()

    auth_type = d['auth_type']

    if auth_type not in ['PASSWORD', 'PHONE', 'APPLE_ID', 'GOOGLE_ID']:
        return bad_request("LoginFailure", "unsupported authentication method")

    user = None
    config = flask.current_app.config
    account_manager = AccountManager(secure_auth.db, config)

    if auth_type == 'PASSWORD':
        email = d['email']
        password = d['password']

        user = account_manager.login_by_password(email, password)

        if user is None:
            return bad_request("LoginFailure", "unknown login failure")

        resp = {}
        resp['userid'] = user.public_id

        token_manager = TokenManager(secure_auth.db)
        (access_token, refresh_token) = token_manager.start_new_session(user.id)
        resp['access_token'] = access_token
        resp['refresh_token'] = refresh_token

        return resp
    elif auth_type == 'PHONE':
        phone = d['phone']

        user = account_manager.login_by_phone(phone)
        if user is None:
            return bad_request("LoginFailure", "unknown login failure")

        resp = {}
        resp['userid'] = user.public_id
        resp['phone'] = user.phone
        return resp
    elif auth_type == 'GOOGLE_ID':
        # TODO: implement later
        user = {}
        user['emai'] = d['email']
    elif auth_type == 'APPLE_ID':
        # TODO: implement later
        user = {}
        user['emai'] = d['email']

    return d


@bp.route('/auth/verify_sms', methods=['POST'])
def verify_sms():
    d = request.get_json()

    phone = d['phone']
    token = d['token']
    public_id = d['userid']

    config = flask.current_app.config
    account_manager = AccountManager(secure_auth.db, config)
    user = account_manager.login_verify_sms(phone, token)

    if user.public_id != public_id:
        raise AppException("LoginFailure", "SMSVerifyFailure", "invalid user account")

    resp = {}
    resp['userid'] = user.public_id

    token_manager = TokenManager(secure_auth.db)
    (access_token, refresh_token) = token_manager.start_new_session(user.id)

    resp['access_token'] = access_token
    resp['refresh_token'] = refresh_token

    return resp


@bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    d = request.get_json()

    refresh_token = d['refresh_token']
    access_token_jwt = get_jwt()

    token_manager = TokenManager(secure_auth.db)
    token_manager.logout_token(refresh_token, access_token_jwt)

    return {'message': 'logout successful'}


@bp.route('/auth/password', methods=['POST'])
@jwt_required(fresh=True)
def change_password():
    d = request.get_json()
    oldpassword = d['oldpassword']
    newpassword = d['newpassword']

    config = flask.current_app.config
    account_manager = AccountManager(secure_auth.db, config)

    userid = get_jwt_identity()
    account_manager.change_password(userid, oldpassword, newpassword)

    return {"message": 'changed password successfully'}


@bp.route('/auth/op', methods=['POST'])
@jwt_required()
def op():
    return {"message": 'test op successful'}


@bp.route('/auth/op2', methods=['POST'])
@jwt_required(fresh=True)
def op2():
    return {"message": 'test op2 successful'}


@bp.route('/auth/logout_all_other_sessions', methods=['POST'])
@jwt_required(fresh=True)
def logout_all_other_sessions():
    d = request.get_json()
    refresh_token = d['refresh_token']
    access_token_jwt = get_jwt()

    # logout all other sessions except for current one
    token_manager = TokenManager(secure_auth.db)
    token_manager.logout_all_other_sessions(access_token_jwt, refresh_token)

    return {'message': 'logout all other sessions successful'}


# We are using the `refresh=True` options in jwt_required to only allow
# refresh tokens to access this route.
@bp.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    token_manager = TokenManager(secure_auth.db)
    (access_token, refresh_token) = token_manager.refresh_tokens(get_jwt())

    resp = {}
    resp['access_token'] = access_token
    resp['refresh_token'] = refresh_token

    return resp


# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt):
    if jwt['type'] == 'refresh':
        return error_response(401, "RefreshTokenExpired", message="The refresh_token is expired. Please login again")
    else:
        return error_response(401, "AccessTokenExpired",
                              message="The token is expired. Please refresh the access token")


# Using the needs_fresh_token_loader decorator, it will call
# this function when a fresh token is required but the token
# is not freshed anymore
@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return error_response(401, "FreshTokenRequired", message="The token is not fresh.")


# Check if the token is invalid.
# Token policy:
#   access token: either don't check and let it expired (expiration should be short)
#                 or check it against cache
#   refresh token: the expiration of refresh_token is relatively longer (30 or 60 days)
#                 it checks against DB whether the stoken is still active or not
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    token_manager = TokenManager(secure_auth.db)
    return token_manager.check_if_token_revoked(jwt_payload)


@bp.app_errorhandler(AppException)
def handle_app_exception(e):
    log.warning("Exception caught: %s, %s" % (e.__class__.__name__, str(e)))
    return error_response(400, e.category, failure_reason=e.error, message=str(e))


@bp.app_errorhandler(exc.IntegrityError)
@bp.app_errorhandler(KeyError)
@bp.app_errorhandler(TypeError)
@bp.app_errorhandler(Exception)
def handle_exception(e):
    log.warning("Exception caught: %s, %s" % (e.__class__.__name__, str(e)))
    return bad_request(e.__class__.__name__, str(e))
