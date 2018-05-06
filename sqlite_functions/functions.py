import regex as re

import util


def sqlite_regexp(expression, string):
    result = re.search(expression, string, re.IGNORECASE)
    return (result is not None)


def wildcard_match(string, pattern):
    if '*' not in pattern:
        return string.lower() == pattern.lower()

    regexp = util.wildcard_to_regexp(pattern)

    return (re.search(regexp, string, re.IGNORECASE) is not None)
