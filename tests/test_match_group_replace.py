import re
import unittest

import match_group_replace


STRING = 'string'
REGEX = 'regex'
REPLACE = 'replace'
RESULT = 'result'

MATCH_GROUP_REPLACE = [
    {
        STRING: 'this is a test',
        REGEX: re.compile(r'this (?P<one>[a-z]+) (?P<two>[a-z]+) ([a-z]+) ?(?P<four>[a-z]+)?'),
        REPLACE: lambda match, idx, _: match[idx].upper() if match[idx] else '',
        RESULT: 'this IS A TEST'
    },
    {
        STRING: 'abcxxxdef',
        REGEX: re.compile(r'([a-wyz]+)(x*)([a-wyz]+)'),
        REPLACE: lambda match, idx, _: ( match[idx] if match[idx][0] == 'x' else match[idx].upper() ) if match[idx] else '',
        RESULT: 'ABCxxxDEF'
    },
    {
        STRING: 'abcdef',
        REGEX: re.compile(r'([a-wyz]+)(x*)([a-wyz]+)'),
        REPLACE: lambda match, idx, _: ( match[idx] if match[idx][0] == 'x' else match[idx].upper() ) if match[idx] else '',
        RESULT: 'ABCDEF'
    },
]


class MatchGroupReplaceTest(unittest.TestCase):
    def test_match_group_replace(self):
        for entry in MATCH_GROUP_REPLACE:
            self.assertEqual(
                match_group_replace.match_group_replace(
                    entry[REGEX],
                    entry[STRING],
                    entry[REPLACE]
                ),
                entry[RESULT]
            )
