import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_INTEGER = [
    {
        VALUE: None,
        SCHEMA: {
            'type': 'integer'
        },
        RESULT: 0
    },
    {
        VALUE: 42,
        SCHEMA: {
            'type': 'integer'
        },
        RESULT: 42
    },
    {
        VALUE: 32,
        SCHEMA: {
            'type': 'integer',
            'minimum': 30
        },
        RESULT: 32
    },
    {
        VALUE: 24,
        SCHEMA: {
            'type': 'integer',
            'maximum': 30
        },
        RESULT: 24
    },
    {
        VALUE: 37,
        SCHEMA: {
            'type': 'integer',
            'exclusiveMinimum': 30
        },
        RESULT: 37
    },
    {
        VALUE: 18,
        SCHEMA: {
            'type': 'integer',
            'exclusiveMaximum': 30
        },
        RESULT: 18
    },
    {
        VALUE: 21,
        SCHEMA: {
            'type': 'integer',
            'multipleOf': 7
        },
        RESULT: 21
    },
]

BUILD_INTEGER_FAIL = [
    {
        VALUE: 'abc',
        SCHEMA: {
            'type': 'integer'
        }
    },
    {
        VALUE: 12.3,
        SCHEMA: {
            'type': 'integer'
        }
    },
    {
        VALUE: 10,
        SCHEMA: {
            'type': 'integer',
            'minimum': 30
        }
    },
    {
        VALUE: 50,
        SCHEMA: {
            'type': 'integer',
            'maximum': 30
        }
    },
    {
        VALUE: 30,
        SCHEMA: {
            'type': 'integer',
            'exclusiveMinimum': 30
        },
    },
    {
        VALUE: 30,
        SCHEMA: {
            'type': 'integer',
            'exclusiveMaximum': 30
        },
    },
    {
        VALUE: 22,
        SCHEMA: {
            'type': 'integer',
            'multipleOf': 7
        }
    },
]


class IntegerTest(unittest.TestCase):
    def test_build_integer(self):
        for entry in BUILD_INTEGER:
            self.assertEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_integer_fail(self):
        for entry in BUILD_INTEGER_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])
