import re
import unittest

import group_index


STRING = 'string'
REGEX = 'regex'
RESULT = 'result'
ARG = 'arg'

GET_NAMED_GROUP_INDEX_DICT = [
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

GET_NAMED_GROUP_INDEX_LIST = [
    {
        STRING: 'this is a test',
        REGEX: re.compile(r'this (?P<one>[a-z]+) (?P<two>[a-z]+) ([a-z]+) ?(?P<four>[a-z]+)?'),
        RESULT: [None, 'one', 'two', None, 'four']
    },
]

GET_NAMED_GROUP_INDEX = [
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

GET_NAMED_GROUP_AT_INDEX = [
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


class GroupIndexTest(unittest.TestCase):
    def test_get_named_group_index_dict(self):
        for entry in GET_NAMED_GROUP_INDEX_DICT:
            self.assertDictEqual(
                group_index.get_named_group_index_dict(entry[REGEX].search(entry[STRING])),
                entry[RESULT]
            )

    def test_get_named_group_index_list(self):
        for entry in GET_NAMED_GROUP_INDEX_LIST:
            self.assertListEqual(
                group_index.get_named_group_index_list(entry[REGEX].search(entry[STRING])),
                entry[RESULT]
            )

    def test_get_named_group_index(self):
        for entry in GET_NAMED_GROUP_INDEX:
            self.assertEqual(
                group_index.get_named_group_index(entry[REGEX].search(entry[STRING]), entry[ARG]),
                entry[RESULT]
            )

    def test_get_named_group_at_index(self):
        for entry in GET_NAMED_GROUP_AT_INDEX:
            self.assertEqual(
                group_index.get_named_group_at_index(entry[REGEX].search(entry[STRING]), entry[ARG]),
                entry[RESULT]
            )
