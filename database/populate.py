#!/usr/bin/env python
# vim: et ts=4 sw=4

import sqlite3
import regex as re
import util

def write_rulesets(rulesets, database_file):
    conn = sqlite3.connect(database_file)
    for ruleset in rulesets:
        if ruleset['default_off'] is not None:
            enabled = False
        else:
            enabled = True

        c = conn.cursor()
        c.execute('''
            INSERT INTO rulesets (name, enabled, disabled_reason)
            VALUES (?, ?, ?)''',
            (ruleset['name'], enabled, ruleset['default_off']))
        ruleset_id = c.lastrowid

        for target in ruleset['targets']:
            regexp = util.wildcard_to_regexp(target)
            c.execute('''
                INSERT INTO targets (ruleset_id, target, target_regexp)
                VALUES (?, ?, ?)''',
                (ruleset_id, target, regexp))

        for exclusion in ruleset['exclusions']:
            c.execute('''
                INSERT INTO exclusions (ruleset_id, exclusion)
                VALUES (?, ?)''',
                (ruleset_id, exclusion))

        for test in ruleset['tests']:
            c.execute('''
                INSERT INTO tests (ruleset_id, test)
                VALUES (?, ?)''',
                (ruleset_id, test))

        for rule in ruleset['rules']:
            # We only substitute the backreferences in the 'to' attribute.
            # I'm sure there are more differences between ECMA and Python REs.
            replacement = re.sub(r'\$([0-9]+)', r'\\\1', rule['to'])
            c.execute('''
                INSERT INTO rules (ruleset_id, rule_from, rule_to, rule_to_py, rule_order)
                VALUES (?, ?, ?, ?, ?)''',
                (ruleset_id, rule['from'], rule['to'], replacement, rule['order']))

        conn.commit()
