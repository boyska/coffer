import os.path

from flask import Flask, jsonify, abort
from flask_appconfig import AppConfig
from gevent.wsgi import WSGIServer
import gevent.monkey


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
        if app.config['ONE']:
            fnames.remove(fname)
        with open(fname) as buf:
            return buf.read()

    return app


def serve(app):
    gevent.monkey.patch_all()

    if app.config['DEBUG']:
        from werkzeug.debug import DebuggedApplication
        app = DebuggedApplication(app)
    http_server = WSGIServer(('0.0.0.0', 0), app)
    http_server.start()
    return http_server


def get_parser():
    from argparse import ArgumentParser
    p = ArgumentParser(description='share files, easily as a coffee')
    sub = p.add_subparsers(title='subcommands')
    send_p = sub.add_parser('send', help="Offer files on the network")
    send_p.set_defaults(func=send_main)
    send_p.add_argument('file', nargs='+')
    send_p.add_argument('--one', action='store_true', default=False)
    get_p = sub.add_parser('get', help="Receive files from the network")
    get_p.add_argument('--all', action='store_true', default=False)
    get_p.set_defaults(func=get_main)

    return p


def send_main(args):
    app = create_app(args.file)
    if args.one:
        app.config['ONE'] = True
    http_server = serve(app)
    address, port = http_server.address
    from avahi_utils import announce
    announce(address, port)
    gevent.wait()


def get_main(args):
    raise NotImplementedError()


if __name__ == '__main__':
    args = get_parser().parse_args()
    print args
    args.func(args)
