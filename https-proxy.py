#!/usr/bin/env python
# vim: et ts=4 sw=4

import sqlite3
import lxml.etree
import logging
import regex as re
import logging
import shutil
import time
import sys
import os

import sqlite_functions
import rulesets
import database
import cache
import util
import config
import http.server

proxy_config = config.ProxyConfiguration()

conn = sqlite3.connect(proxy_config.get('database'))
conn.create_function('regexp', 2, sqlite_functions.sqlite_regexp)
conn.create_function('wildcard_match', 2, sqlite_functions.wildcard_match)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

def rebuild_database():
    db_file = proxy_config.get('database')
    db_persist = proxy_config.get('database_persist')

    rules = proxy_config.get('rules')
    rules_extensions = proxy_config.get('rule_extensions').split(',')

    database.schema.create_schema(db_file)
    sets = rulesets.parse.parse_rulesets(rules, rules_extensions)
    database.populate.write_rulesets(sets, db_file)

    # Not sure if you can actually do this, but stuff *should* be on disk.
    shutil.copyfile(db_file, db_persist)

if __name__ == '__main__':
    db_file = proxy_config.get('database')
    db_persist = proxy_config.get('database_persist')

    if not os.path.isfile(db_file) or os.path.getsize(db_file) == 0:
        if os.path.isfile(db_persist) and os.path.getsize(db_persist) > 1:
            logger.info('Copying persistent database (%s) to working location %s',
                db_persist, db_file)
            shutil.copyfile(db_persist, db_file)
        else:
            rebuild_database()

    logger.info('Building cache ...')
    start_time = time.time()
    cache.cache.populate(conn)
    end_time = time.time()
    logger.info('Cache built in %.10f seconds.' % (end_time - start_time))

    if 0:
        c = conn.cursor()
        c.execute('SELECT ruleset_id, test FROM tests LIMIT 50')
        res = c.fetchall()
        for i in range(0, 3):
            for r in res:
                start_time = time.time()
                rules = cache.cache.apply_rules(r[1])
                end_time = time.time()
                print('Took: %.10f' % (end_time - start_time))

    server = http.server.Server(('', 8000))
    server.serve()
