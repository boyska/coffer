'''
This module contains a (hopefully) thin layer that adds a CLI interface to
coffer.
'''
from __future__ import print_function
import re
import sys
import logging

import server
import client


def send_main(args):
    conf = {}
    if args.one:
        conf['ONE'] = True
    if args.password:
        conf['PASSWORD'] = args.password
    server.send(args.file, conf)


def get_main(args):
    offers = [url for offer_id, url in client.get_offers(args.password)
              if re.search(args.filter, offer_id)]
    if not offers:
        sys.stderr.write("No offers found\n")
        return
    if args.list_only:
        for url in offers:
            print(url)
        sys.exit(0)
    if args.all or len(offers) == 1:
        for url in offers:
            handle_url(args, url)
    else:  # more than one offer, and no --all
        for i, offer in enumerate(offers):
            print('[%d]\t%s' % (i, offer))
        print('Type the IDs you want to download, separated by spaces')
        ids = map(int, raw_input().split())
        for i in ids:
            handle_url(args, offers[i])


def handle_url(args, url):
    response = client.dl_offer(url, args.password)
    if response.status_code != 200:
        logging.warning('Error downloading %s' % url)
        return
    if args.cat:
        sys.stdout.write(response.text)
    else:
        # TODO: download!
        raise NotImplementedError('--cat is the only implemented way')


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
    get_p.add_argument('--password', metavar='PASS', default=None,
                       help="Provide password authentication")
    sel = get_p.add_argument_group(
        title='selection',
        description="Which files should we consider?")
    sel.add_argument('--filter', metavar='REGEXP', default='',
                     help="filter to files whose filename matches REGEXP. "
                     "It comes before --all")
    sel.add_argument('--all', action='store_true', default=False,
                     help="Download every matching file, without asking")
    dl = get_p.add_argument_group(title="download",
                                  description="File downloading handling")
    dl.add_argument('--list-only', action='store_true', default=False,
                    help="Don't download, just print urls")
    dl.add_argument('--cat',
                    help='Output every downloaded offer, concatenated',
                    action='store_true', dest='cat', default=False)
    get_p.set_defaults(func=get_main)

    return p


def main():
    logging.basicConfig(level=logging.WARN)
    logging.getLogger('requests').setLevel(logging.ERROR)
    args = get_parser().parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
