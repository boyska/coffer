import sys
import os.path
import logging
import socket

import requests

from flask import Flask, jsonify, abort, Response
from flask_appconfig import AppConfig
from gevent.wsgi import WSGIServer
import gevent.monkey


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
    get_p.add_argument('--filter', metavar='REGEXP', default=None)
    get_p.add_argument('--password', metavar='PASS', default=None)
    get_p.add_argument('--cat', help='Output every downloaded offer',
                       action='store_true', dest='cat', default=False)
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
    gevent.wait(count=1)


def get_offers(args):
    from avahi_utils import discover
    peers = discover()
    for p in peers:
        base = 'http://%s:%s' % (socket.inet_ntoa(p.address), p.port)
        try:
            r = requests.get('%s/offers' % base, timeout=5)
        except:
            logging.warning("Failure for %s" % base)
            continue
        peer_offers = r.json()['offers']
        for offer_id in peer_offers:
            # TODO: if matches args.filter
            url = '%s/offers/%s' % (base, offer_id)
            logging.debug('Selecting %s as candidate' % url)
            yield url


def dl_offer(args, url):
    auth = None
    if args.password is not None:
        auth = ('user', args.password)
    return requests.get(url, auth=auth, timeout=5)


def get_main(args):
    offers = tuple(get_offers(args))
    if args.all or len(offers) == 1:
        for url in offers:
            response = dl_offer(args, url)
            if response.status_code != 200:
                logging.warning('Error downloading %s' % url)
            if args.cat:
                sys.stdout.write(response.text)
            else:
                # TODO: download!
                raise NotImplementedError('--cat is the only implemented way')
    else:  # more than one offer, and no --all
        raise NotImplementedError('choose what you want')


if __name__ == '__main__':
    args = get_parser().parse_args()
    args.func(args)
