#!/usr/bin/env python
# vim: et ts=4 sw=4


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
