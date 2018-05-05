#!/usr/bin/env python
# vim: et ts=4 sw=4

import sqlite3
import collections
import lxml.etree
import urlparse
import logging
import regex as re
import time
import sys
import os

# There doesn't seem to be an XSD so just do some rudimentary
# validation here.
def valid_ruleset(ruleset):
    if len(ruleset['targets']) < 1:
        return False
    elif len(ruleset['rules']) < 1:
        return False

    return True

def parse_rulesets(rule_path, valid_extensions):
    parser = lxml.etree.XMLParser()
    rulefiles = os.listdir(rule_path)
    rulesets = list()
    stats = collections.defaultdict(int)
    i = 0

    for rulefile in rulefiles:
        _, e = os.path.splitext(rulefile)
        if e not in valid_extensions: continue
        sys.stdout.write('Parsing rule file %d/%d\r' % (i, len(rulefiles)))
        i += 1
#        if i > 1000: break

        try:
            tree = lxml.etree.parse(os.path.join(rule_path, rulefile), parser)
        except:
            stats['invalid'] += 1
            continue

        if tree.getroot().tag != 'ruleset':
            stats['invalid'] += 1
            continue

        ruleset = {}
        ruleset['name'] = tree.getroot().get('name')
        ruleset['default_off'] = tree.getroot().get('default_off')
        ruleset['targets'] = list()
        for target in tree.getroot().findall('target'):
            ruleset['targets'].append(target.get('host'))

        ruleset['rules'] = list()
        for rule in tree.getroot().findall('rule'):
            ruleset['rules'].append(rule)

        ruleset['exclusions'] = list()
        for exclusion in tree.getroot().findall('exclusion'):
            ruleset['exclusions'].append(exclusion.get('pattern'))

        ruleset['tests'] = list()
        for test in tree.getroot().findall('test'):
            ruleset['tests'].append(test.get('url'))

        # Cookie rewriting not implemented

        ruleset['rules'] = list()
        for rule in tree.getroot().findall('rule'):
            r = {}
            r['from'] = rule.get('from')
            r['to'] = rule.get('to')
            r['order'] = len(ruleset['rules'])
            ruleset['rules'].append(r)

        if not valid_ruleset(ruleset):
            stats['invalid'] += 1
            continue

        rulesets.append(ruleset)
    
    print('Valid rulesets: %d' % (stats['valid']))
    print('Invalid rulesets: %d' % (stats['invalid']))

    return rulesets
