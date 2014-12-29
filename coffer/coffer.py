import sys
import logging
import socket

import requests

from gevent.wsgi import WSGIServer
import gevent.monkey

from webapp import create_app


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
    send_p.add_argument('--password', metavar='PASS', default=None)
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
    if args.password:
        app.config['PASSWORD'] = args.password
    http_server = serve(app)
    address, port = http_server.address
    from avahi_utils import announce
    announce(address, port)
    gevent.wait(count=1)


def get_auth(args):
    if args.password is not None:
        return ('user', args.password)
    return None


def get_offers(args):
    from avahi_utils import discover
    peers = discover()
    for p in peers:
        base = 'http://%s:%s' % (socket.inet_ntoa(p.address), p.port)
        try:
            response = requests.get('%s/offers' % base, timeout=5,
                                    auth=get_auth(args))
        except:
            logging.warning("Failure for %s" % base)
            continue
        if response.status_code == 401:
            logging.warning('Wrong password for %s' % base)
            continue
        elif response.status_code != 200:
            logging.warning('Failure (%d) for %s' %
                            (response.status_code, base))
            continue
        peer_offers = response.json()['offers']
        for offer_id in peer_offers:
            # TODO: if matches args.filter
            url = '%s/offers/%s' % (base, offer_id)
            logging.debug('Selecting %s as candidate' % url)
            yield url


def dl_offer(args, url):
    return requests.get(url, auth=get_auth(args), timeout=5)


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
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('requests').setLevel(logging.ERROR)
    args = get_parser().parse_args()
    args.func(args)
