'''
This module contains functions for discovery, downloading, etc
'''
import logging
import socket

import requests

from zeroconf_utils import discover


def get_auth(password=None):
    if password is not None:
        return ('user', password)
    return None


def get_offers(password=None):
    peers = discover()
    for p in peers:
        base = 'http://%s:%s' % (socket.inet_ntoa(p.address), p.port)
        try:
            response = requests.get('%s/offers' % base, timeout=5,
                                    auth=get_auth(password))
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
            url = '%s/offers/%s' % (base, offer_id)
            logging.debug('Selecting %s as candidate' % url)
            yield offer_id, url


def dl_offer(url, password=None):
    return requests.get(url, auth=get_auth(password), timeout=5)
