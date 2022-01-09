import re
import unittest

from src.pycolor import group_index

STRING = 'string'
REGEX = 'regex'
RESULT = 'result'
ARG = 'arg'

class GroupIndexTest(unittest.TestCase):
    def test_get_named_group_index_dict(self):
        entries = [
            {
                STRING: 'this is a test',
                REGEX: re.compile(r'this (?P<one>[a-z]+) (?P<two>[a-z]+) ([a-z]+) ?(?P<four>[a-z]+)?'),
                RESULT: {
                    1: 'one',
                    2: 'two',
                    4: 'four'
                }
            },
        ]

        for entry in entries:
            regex = entry[REGEX]
            string = entry[STRING]
            with self.subTest(regex=regex, string=string):
                self.assertDictEqual(
                    entry[RESULT],
                    group_index.get_named_group_index_dict(regex.search(string)),
                )

    def test_get_named_group_index_list(self):
        entries = [
            {
                STRING: 'this is a test',
                REGEX: re.compile(r'this (?P<one>[a-z]+) (?P<two>[a-z]+) ([a-z]+) ?(?P<four>[a-z]+)?'),
                RESULT: [None, 'one', 'two', None, 'four']
            },
        ]

        for entry in entries:
            regex = entry[REGEX]
            string = entry[STRING]
            with self.subTest(regex=regex, string=string):
                self.assertListEqual(
                    entry[RESULT],
                    group_index.get_named_group_index_list(regex.search(string))
                )

    def test_get_named_group_index(self):
        entries = [
            {
                STRING: 'this is a test',
                REGEX: re.compile(r'this (?P<one>[a-z]+) (?P<two>[a-z]+) ([a-z]+) ?(?P<four>[a-z]+)?'),
                ARG: 'two',
                RESULT: 2
            },
            {
                STRING: 'this is a test',
                REGEX: re.compile(r'this (?P<one>[a-z]+) (?P<two>[a-z]+) ([a-z]+) ?(?P<four>[a-z]+)?'),
                ARG: 'invalid',
                RESULT: None
            }
        ]

        for entry in entries:
            regex = entry[REGEX]
            string = entry[STRING]
            arg = entry[ARG]
            with self.subTest(regex=regex, string=string, arg=arg):
                self.assertEqual(
                    entry[RESULT],
                    group_index.get_named_group_index(regex.search(string), arg)
                )

    def test_get_named_group_at_index(self):
        entries = [
            {
                STRING: 'this is a test',
                REGEX: re.compile(r'this (?P<one>[a-z]+) (?P<two>[a-z]+) ([a-z]+) ?(?P<four>[a-z]+)?'),
                ARG: 2,
                RESULT: 'two'
            },
            {
                STRING: 'this is a test',
                REGEX: re.compile(r'this (?P<one>[a-z]+) (?P<two>[a-z]+) ([a-z]+) ?(?P<four>[a-z]+)?'),
                ARG: 100,
                RESULT: None
            },
        ]

        for entry in entries:
            regex = entry[REGEX]
            string = entry[STRING]
            arg = entry[ARG]
            with self.subTest(regex=regex, string=string, arg=arg):
                self.assertEqual(
                    entry[RESULT],
                    group_index.get_named_group_at_index(regex.search(string), arg)
                )
