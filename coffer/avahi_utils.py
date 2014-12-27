#! /usr/bin/env python
import socket
import atexit
import logging

from zeroconf import ServiceInfo, Zeroconf

log = logging.getLogger('avahi-utils')


def get_my_ip():
    return socket.gethostbyname(socket.gethostname())


def announce(address, port, service_type='_coffer._tcp.local.'):
    if address == '0.0.0.0':
        address = get_my_ip()
    info = ServiceInfo(service_type, 'Coffer.%s' % service_type,
                       socket.inet_aton(address), port, 0, 0,
                       {})
    z = Zeroconf()
    z.register_service(info)

    def _close():
        log.info('Closing...')
        z.unregister_service(info)
        z.close()
    atexit.register(_close)
    return info
