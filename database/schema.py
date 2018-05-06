#!/usr/bin/env python
# vim: et ts=4 sw=4

import sqlite3


def create_schema(database_file):
    connection = sqlite3.connect(database_file)
    c = connection.cursor()

    c.execute('''
        CREATE TABLE rulesets
            (id INTEGER PRIMARY KEY,
             name TEXT NOT NULL DEFAULT "Unnamed Ruleset",
             enabled INTEGER NOT NULL DEFAULT 0,
             disabled_reason TEXT)''')
    c.execute('''
        CREATE TABLE targets
            (id INTEGER PRIMARY KEY,
             ruleset_id INTEGER,
             target TEXT,
             target_regexp TEXT,
             FOREIGN KEY(ruleset_id) REFERENCES rulesets(id))
    ''')
    c.execute('''
        CREATE TABLE exclusions
            (id INTEGER PRIMARY KEY,
             ruleset_id INTEGER,
             exclusion TEXT,
             FOREIGN KEY(ruleset_id) REFERENCES rulesets(id))
    ''')
    c.execute('''
        CREATE TABLE tests
            (id INTEGER PRIMARY KEY,
             ruleset_id INTEGER,
             test TEXT,
             FOREIGN KEY(ruleset_id) REFERENCES rulesets(id))
    ''')
    c.execute('''
        CREATE TABLE rules
            (id INTEGER PRIMARY KEY,
             ruleset_id INTEGER,
             rule_from TEXT,
             rule_to TEXT,
             rule_to_py TEXT,
             rule_order INTEGER,
             FOREIGN KEY(ruleset_id) REFERENCES rulesets(id))
    ''')
    connection.commit()
