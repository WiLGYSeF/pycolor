import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_NUMBER = [
    {
        VALUE: None,
        SCHEMA: {
            'type': 'number'
        },
        RESULT: 0
    },
    {
        VALUE: 12.3,
        SCHEMA: {
            'type': 'number'
        },
        RESULT: 12.3
    },
    {
        VALUE: 32.6,
        SCHEMA: {
            'type': 'number',
            'minimum': 30.4
        },
        RESULT: 32.6
    },
    {
        VALUE: 24,
        SCHEMA: {
            'type': 'number',
            'maximum': 30
        },
        RESULT: 24
    },
    {
        VALUE: 37,
        SCHEMA: {
            'type': 'number',
            'exclusiveMinimum': 30
        },
        RESULT: 37
    },
    {
        VALUE: 18,
        SCHEMA: {
            'type': 'number',
            'exclusiveMaximum': 30
        },
        RESULT: 18
    },
    {
        VALUE: 21,
        SCHEMA: {
            'type': 'number',
            'multipleOf': 7
        },
        RESULT: 21
    },
]

BUILD_NUMBER_FAIL = [
    {
        VALUE: 'abc',
        SCHEMA: {
            'type': 'number'
        }
    },
    {
        VALUE: 10,
        SCHEMA: {
            'type': 'number',
            'minimum': 30
        }
    },
    {
        VALUE: 50,
        SCHEMA: {
            'type': 'number',
            'maximum': 30
        }
    },
    {
        VALUE: 30,
        SCHEMA: {
            'type': 'number',
            'exclusiveMinimum': 30
        },
    },
    {
        VALUE: 30,
        SCHEMA: {
            'type': 'number',
            'exclusiveMaximum': 30
        },
    },
    {
        VALUE: 22,
        SCHEMA: {
            'type': 'number',
            'multipleOf': 7
        },
        RESULT: ValueError
    },
]


class NumberTest(unittest.TestCase):
    def test_build_number(self):
        for entry in BUILD_NUMBER:
            self.assertEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_number_fail(self):
        for entry in BUILD_NUMBER_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])
