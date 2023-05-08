from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, error, **kwargs):
    payload = {'error': error, 'http_code': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    for key, value in kwargs.items():
        if key == 'exception':
            ex = value
            payload[key] = {'exception': ex.__class__.__name__, 'message': str(ex)}
        else:
            payload[key] = value

    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(error, message, exception=None):
    return error_response(400, error, message=message, exception=exception)
