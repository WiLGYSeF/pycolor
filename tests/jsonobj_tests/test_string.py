import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_STRING = [
    {
        VALUE: None,
        SCHEMA: {
            'type': 'string'
        },
        RESULT: ''
    },
    {
        VALUE: 'abc',
        SCHEMA: {
            'type': 'string'
        },
        RESULT: 'abc'
    },
    {
        VALUE: 'abcdef',
        SCHEMA: {
            'type': 'string',
            'minLength': 4
        },
        RESULT: 'abcdef'
    },
    {
        VALUE: 'abcde',
        SCHEMA: {
            'type': 'string',
            'maxLength': 5
        },
        RESULT: 'abcde'
    },
    {
        VALUE: 'abc[123]def',
        SCHEMA: {
            'type': 'string',
            'pattern': r'[a-z]{3}\[[0-9]{3}\][a-z]{3}'
        },
        RESULT: 'abc[123]def'
    },
]

BUILD_STRING_FAIL = [
    {
        VALUE: 1234,
        SCHEMA: {
            'type': 'string'
        }
    },
    {
        VALUE: 'acbdef',
        SCHEMA: {
            'type': 'string',
            'minLength': 8
        }
    },
    {
        VALUE: 'abcde',
        SCHEMA: {
            'type': 'string',
            'maxLength': 2
        }
    },
    {
        VALUE: '123[abc]456',
        SCHEMA: {
            'type': 'string',
            'pattern': r'[a-z]{3}\[[0-9]{3}\][a-z]{3}'
        }
    },
]


class StringTest(unittest.TestCase):
    def test_build_string(self):
        for entry in BUILD_STRING:
            self.assertEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_string_fail(self):
        for entry in BUILD_STRING_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])
