import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_STRING_ARRAY = [
    {
        VALUE: None,
        SCHEMA: {
            'type': 'string_array'
        },
        RESULT: ''
    },
    {
        VALUE: 'abc',
        SCHEMA: {
            'type': 'string_array'
        },
        RESULT: 'abc'
    },
    {
        VALUE: ['abc', 'd', 'ef'],
        SCHEMA: {
            'type': 'string_array'
        },
        RESULT: 'abcdef'
    },
    {
        VALUE: ['abc', 'd', 'ef'],
        SCHEMA: {
            'type': 'string_array',
            'minLength': 4
        },
        RESULT: 'abcdef'
    },
    {
        VALUE: ['abc', 'de'],
        SCHEMA: {
            'type': 'string_array',
            'maxLength': 5
        },
        RESULT: 'abcde'
    }
]

BUILD_STRING_ARRAY_FAIL = [
    {
        VALUE: 1234,
        SCHEMA: {
            'type': 'string_array'
        }
    },
    {
        VALUE: ['acb', 'def'],
        SCHEMA: {
            'type': 'string_array',
            'minLength': 8
        }
    },
    {
        VALUE: ['abcde'],
        SCHEMA: {
            'type': 'string_array',
            'maxLength': 2
        }
    }
]


class StringArrayTest(unittest.TestCase):
    def test_build_string_array(self):
        for entry in BUILD_STRING_ARRAY:
            self.assertEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_string_array_fail(self):
        for entry in BUILD_STRING_ARRAY_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])
