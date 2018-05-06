#!/usr/bin/env python
# vim: et ts=4 sw=4

import sqlite3
import logging
import shutil
import sys
import os

import sqlite_functions
import rulesets
import database
import cache
import config
import util
import http.server

proxy_config = config.Configuration
logger = logging.getLogger()


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


# https://github.com/EFForg/https-everywhere/blob/ad4c68ba627858a6e9755f05979e7ed8761fe346/ruleset-testing.md
# Since we run these tests through the entire application, the part about
# only matching 1 rule or exclusion is ignored.
#
# Expected test results aren't really obvious. We can't assert an output
# value. So we just run the tests and see if anything explodes.
#
def run_tests(connection, iterations=1):
    c = connection.cursor()

    # Implicit tests
    c.execute('SELECT target FROM targets')
    res = c.fetchall()
    test_urls = ['http://%s/' % (t[0]) for t in res]
    logger.info('Running %d implicit tests, %d iterations' % (len(test_urls),
                                                              iterations))

    # Explicit tests
    c.execute('SELECT test FROM tests')
    res = c.fetchall()
    test_urls.append([t[0] for t in res])
    logger.info('Running %d explicit tests, %d iterations' % (len(res),
                                                              iterations))

    for i in range(0, iterations):
        for test_url in test_urls:
            timer = util.Timer()
            timer.start_timer('Applying rules for %s' % test_url)
            result_url = cache.cache.apply_rules(test_url)
            timer.end_timer('Done. %s -> %s (took {.10f} sec)' %
                            (test_url, result_url))

    c.close()

def copy_persistent():
    if proxy_config['database_persist'].lower() == 'off':
        logger.info('Not copying persistent database.')
        return

    logger.info('Copying persistent database (%s) to working location %s',
                proxy_config['database_persist'], proxy_config['database'])

    shutil.copyfile(proxy_config['database_persist'], proxy_config['database'])

if __name__ == '__main__':
    rebuild = False
    if proxy_config['action'] == 'update':
        try:
            logger.info('Removing database file %s', proxy_config['database'])
            os.remove(proxy_config['database'])
        except os.IOError as e:
            if e.errno != 2:
                raise e
        rebuild = True

    if not rebuild and (not os.path.isfile(proxy_config['database']) or
       os.path.getsize(proxy_config['database']) == 0):
        if os.path.isfile(proxy_config['database_persist']) and \
           os.path.getsize(proxy_config['database_persist']) > 1:
            copy_persistent()
        else:
            rebuild = True

    conn = sqlite3.connect(proxy_config.get('database'))
    conn.create_function('regexp', 2, sqlite_functions.sqlite_regexp)
    conn.create_function('wildcard_match', 2, sqlite_functions.wildcard_match)

    if rebuild:
        timer = util.Timer()
        timer.start_timer('Rereading rulesets from %s', proxy_config['rules'])
        rebuild_database()
        timer.end_timer('Reread all rulesets. Took {:.10f} seconds.')
        copy_persistent()

    timer = util.Timer()
    timer.start_timer('Reading rulesets into memory ...')
    cache.cache.populate(conn)
    timer.end('Rules loaded in {:.4f} seconds.')

    if proxy_config['action'] == 'test':
        run_tests(conn)
    elif proxy_config['action'] == 'server':
        listen = util.parse_address(proxy_config['listen'])
        try:
            server = http.server.Server(listen)
            server.serve()
        except Exception as e:
            logger.error('Exception happened. Stopping server.')
            logger.error('Exception: %s: %s', sys.exc_info()[0],
                         sys.exc_info()[1])
            if hasattr(e, 'errno'):
                if e.errno == 13 and listen[1] < 1024:
                    logger.error('You must be root to use port %d', listen[1])
