import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_CONST = [
    {
        VALUE: None,
        SCHEMA: {
            'type': 'const',
            'const': 'first'
        },
        RESULT: 'first'
    },
    {
        VALUE: None,
        SCHEMA: {
            'const': 'first'
        },
        RESULT: 'first'
    },
    {
        VALUE: 'first',
        SCHEMA: {
            'const': 'first'
        },
        RESULT: 'first'
    },
]

BUILD_CONST_FAIL = [
    {
        VALUE: 'invalid',
        SCHEMA: {
            'type': 'const',
            'const': 'first'
        }
    },
    {
        VALUE: 'invalid',
        SCHEMA: {
            'const': 'first'
        }
    },
    {
        VALUE: None,
        SCHEMA: {
            'const': 'first',
            'default': 'invalid'
        }
    },
]


class ConstTest(unittest.TestCase):
    def test_build_enum(self):
        for entry in BUILD_CONST:
            self.assertEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_enum_fail(self):
        for entry in BUILD_CONST_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])

    def test_build_const_missing(self):
        with self.assertRaises(KeyError):
            jsonobj.build(None, schema={
                'type': 'const'
            })
