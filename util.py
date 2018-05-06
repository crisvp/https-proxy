#!/usr/bin/env python
# vim: et ts=4 sw=4

import logging
import regex as re
import time

logger = logging.getLogger(__name__)


class Timer():
    def __init__(self, loglevel='DEBUG'):
        self._loglevel = logging.getLevelName(loglevel)
        self._start_time = None
        self._end_time = None

    def start_timer(self, message, *args, **kwargs):
        logger.log(self._loglevel, message, *args, **kwargs)
        self._start_time = time.time()

    def end(self, message, *args, **kwargs):
        self._end_time = time.time()
        logger.log(self._loglevel,
                   message.format(self._end_time - self._start_time),
                   *args, **kwargs)


def parse_address(address):
    # if only 1 colon, assume hostname:port or IPv4:port
    colons = address.count(':')
    if colons == 1:
        [host, port] = address.split(':')
        port = int(port)
        return (host, port)

    match = re.match(r'^\[?([:a-f0-9]+)\]?:([0-9]+)$', address)
    host = match.group(1)
    port = int(match.group(2))

    return (host, port)


def wildcard_to_regexp(wildcard):
    regexp = wildcard
    # Right side wildcard only goes 1 level when after a
    # dot. It is unclear what they do when they don't follow
    # a dot, so those cases are ignored.
    if wildcard[-2:] == '.*':
        regexp = '%s%s' % (wildcard[:-2], '\.[^\.]*$')

    # Left side wildcard matches any number of subdomains
    if wildcard[0:2] == '*.':
        regexp = '%s%s' % ('^.*\.', wildcard[2:])

    # A wildcard somewhere in the middle is unspecified. We'll
    # assume it matches only 1 part.
    regexp.replace('.*.', '\.[^\.]+\.')

    return regexp
