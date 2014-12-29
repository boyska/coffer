import os
import logging
log = logging.getLogger('coffer.webapp')
from functools import wraps

import gevent
from flask import Flask, jsonify, abort, Response, current_app, request
from flask_appconfig import AppConfig


def _gevent_exit():
    raise SystemExit()


def create_app(fnames):
    app = Flask('coffer')
    app.config.update({
        'DEBUG': True,
        'ONE': False,
        'PASSWORD': False,
    })
    AppConfig(app, None, default_settings=False)

    def get_offer_description(file_list):
        return {os.path.basename(f): f for f in file_list}

    @app.route('/offers')
    @requires_auth
    def offers_list():
        return jsonify(dict(offers=get_offer_description(fnames)))

    @app.route('/offers/<offer_id>')
    @requires_auth
    def dl_offer(offer_id):
        fname = get_offer_description(fnames).get(offer_id, None)
        if fname is None:
            return abort(404)

        def stream(filename):
            with open(filename) as buf:
                for line in buf:
                    yield line
            if app.config['ONE']:
                fnames.remove(filename)
                if not fnames:
                    log.info('No more files to serve, terminating')
                    gevent.spawn_later(1, _gevent_exit)
        return Response(stream(fname))

    return app


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'user' and password == current_app.config['PASSWORD']


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if current_app.config['PASSWORD']:
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()
        return f(*args, **kwargs)
    return decorated
