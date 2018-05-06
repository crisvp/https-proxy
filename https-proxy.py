#!/usr/bin/env python
# vim: et ts=4 sw=4

import sqlite3
import logging
import shutil
import os

import sqlite_functions
import rulesets
import database
import cache
import config
import util
import http.server

proxy_config = config.Configuration

conn = sqlite3.connect(proxy_config.get('database'))
conn.create_function('regexp', 2, sqlite_functions.sqlite_regexp)
conn.create_function('wildcard_match', 2, sqlite_functions.wildcard_match)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
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


# https://github.com/EFForg/https-everywhere/blob/ad4c68ba627858a6e9755f05979e7ed8761fe346/ruleset-testing.md
# Since we run these tests through the entire application, the part about
# only matching 1 rule or exclusion is ignored.
#
# Expected test results aren't really obvious. We can't assert an output
# value. So we just run the tests and see if anything explodes.
#
def run_tests(iterations=1):
    c = conn.cursor()

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


if __name__ == '__main__':
    if not os.path.isfile(proxy_config['database']) or \
       os.path.getsize(proxy_config['database']) == 0:
        if os.path.isfile(proxy_config['database_persist']) and \
           os.path.getsize(proxy_config['database_persist']) > 1:
            logger.info(
                'Copying persistent database (%s) to working location %s',
                proxy_config['database_persist'], proxy_config['database'])
            shutil.copyfile(proxy_config['database_persist'],
                            proxy_config['database'])
        else:
            rebuild_database()

    timer = util.Timer()
    timer.start_timer('Loading rulesets ...')
    cache.cache.populate(conn)
    timer.end('Rules loaded in {:.4f} seconds.')

    if proxy_config['action'] == 'test':
        run_tests()
    elif proxy_config['action'] == 'server':
        listen = util.parse_address(proxy_config['listen'])
        server = http.server.Server(listen)
        server.serve()
