import re
import unittest

from src.pycolor.match_group_replace import match_group_replace

STRING = 'string'
REGEX = 'regex'
REPLACE = 'replace'
RESULT = 'result'

class MatchGroupReplaceTest(unittest.TestCase):
    def test_match_group_replace(self):
        entries = [
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

        for entry in entries:
            string = entry[STRING]
            regex = entry[REGEX]
            with self.subTest(string=string, regex=regex):
                self.assertEqual(
                    entry[RESULT],
                    match_group_replace(
                        regex.search(string),
                        entry[REPLACE]
                    )
                )
