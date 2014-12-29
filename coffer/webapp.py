import os
import logging

import gevent
from flask import Flask, jsonify, abort, Response
from flask_appconfig import AppConfig


def _gevent_exit():
    raise SystemExit()


def create_app(fnames):
    app = Flask('coffer')
    app.config.update({
        'DEBUG': True,
        'ONE': False,
    })
    AppConfig(app, None, default_settings=False)

    def get_offer_description(file_list):
        return {os.path.basename(f): f for f in file_list}

    @app.route('/offers')
    def offers_list():
        return jsonify(dict(offers=get_offer_description(fnames)))

    @app.route('/offers/<offer_id>')
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
                    logging.info('No more files to serve, terminating')
                    gevent.spawn_later(1, _gevent_exit)
        return Response(stream(fname))

    return app
