import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_ENUM = [
    {
        VALUE: None,
        SCHEMA: {
            'type': 'enum',
            'enum': ['first', 'second', 'third']
        },
        RESULT: 'first'
    },
    {
        VALUE: None,
        SCHEMA: {
            'enum': ['first', 'second', 'third']
        },
        RESULT: 'first'
    },
    {
        VALUE: None,
        SCHEMA: {
            'enum': ['first', 'second', 'third'],
            'default': 'second'
        },
        RESULT: 'second'
    },
    {
        VALUE: None,
        SCHEMA: {
            'type': 'enum',
            'enum': ['first', 'second', 'third']
        },
        RESULT: 'first'
    },
    {
        VALUE: 'third',
        SCHEMA: {
            'enum': ['first', 'second', 'third']
        },
        RESULT: 'third'
    },
    {
        VALUE: 'third',
        SCHEMA: {
            'type': 'string',
            'enum': ['first', 'second', 'third']
        },
        RESULT: 'third'
    },
]

BUILD_ENUM_FAIL = [
    {
        VALUE: 'invalid',
        SCHEMA: {
            'type': 'enum',
            'enum': ['first', 'second', 'third']
        }
    },
    {
        VALUE: 'invalid',
        SCHEMA: {
            'enum': ['first', 'second', 'third']
        }
    },
    {
        VALUE: None,
        SCHEMA: {
            'enum': ['first', 'second', 'third'],
            'default': 'invalid'
        }
    },
    {
        VALUE: 32,
        SCHEMA: {
            'type': 'string',
            'enum': ['first', 'second', 32]
        }
    },
]


class EnumTest(unittest.TestCase):
    def test_build_enum(self):
        for entry in BUILD_ENUM:
            self.assertEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_enum_fail(self):
        for entry in BUILD_ENUM_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])

    def test_build_enum_missing(self):
        with self.assertRaises(KeyError):
            jsonobj.build(None, schema={
                'type': 'enum'
            })
