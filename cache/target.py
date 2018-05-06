#!/usr/bin/env python
# vim: et ts=4 sw=4

import sqlite3
import collections
import regex as re
import logging
import urlparse
import time
import sys
import os

from . import lru

logger = logging.getLogger(__name__)

class TargetCache:
    def __init__(self, db_connection=None):
        self._target_regexp = list()
        self._target_simple = list()
        self._conn = None

    def populate(self, db_connection=None):
        logger.debug('Populating cache.')
        if db_connection is None:
            db_connection = self._conn
        else:
            self._conn = db_connection

        c = db_connection.cursor()
        c.execute('SELECT ruleset_id, target, target_regexp FROM targets')
        res = c.fetchall()
        for r in res:
            if r[1] == r[2]:
                self._target_simple.append((r[0], r[1]))
            else:
                self._target_regexp.append((r[0], r[1], re.compile(r[2], re.IGNORECASE))) 

        logger.debug('Simple targets: %d, Regexp targets: %d',
            len(self._target_simple), len(self._target_regexp))

        c.close()
    

    # Returns a list of tuples containing ruleset_id and matching target
    @lru.lru_cache(max_size=2000)
    def lookup_rulesets(self, host):
        targets = list()
        for target in self._target_simple:
            if host.endswith(target[1]):
                logger.debug('endswith: %s, matches %s', target[1], host)
                targets.append((target[0], target[1]))

        for target in self._target_regexp:
            if target[2].search(host) is not None:
                logger.debug('regexp: %s, matches %s', target[2], host)
                targets.append((target[0], target[1]))

        return targets

    @lru.lru_cache(max_size=100)
    def apply_rules(self, url):
        parsed = urlparse.urlparse(url)

        # Does it make sense to try to match on anything that is not http?
        # Probably not, even though we technically probably should.
        if parsed.scheme != 'http':
            return url

        # Not sure if rulesets can contain port numbers. Let's assume not.
        if ':' in parsed.netloc:
            host = parsed.netloc.split(':')[0]
        else:
            host = parsed.netloc

        # It is unclear what happens when there are multiple matching
        # rulesets. We'll just apply them all in undefined order.
        matching_rulesets = self.lookup_rulesets(host)
        logger.debug('Matching rulesets: %s', matching_rulesets)

        rules = list()
        exclusions = list()
        c = self._conn.cursor()
        for match in matching_rulesets:
            c.execute('SELECT exclusion FROM exclusions WHERE ruleset_id = ?', (match[0],))
            exclusions = c.fetchall()

            c.execute('SELECT rule_from, rule_to_py FROM rules WHERE ruleset_id = ? ORDER BY rule_order ASC', (match[0],))
            rules = c.fetchall()
        c.close()

        for exclusion in exclusions:
            if re.search(exclusion[0], url) is not None:
                logger.debug('url %s excluded through rule %s', url, exclusion[0])
                return url

        result_url = url
        for rule in rules:
            logger.debug('Applying rule %s', rule)
            result_url = re.sub(rule[0], rule[1], result_url)
            if result_url != url:
                logger.debug('Rule applied: %s -> %s', url, result_url)
                break

        return result_url
