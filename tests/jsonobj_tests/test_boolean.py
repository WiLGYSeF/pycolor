import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_BOOLEAN = [
    {
        VALUE: None,
        SCHEMA: {
            'type': 'boolean'
        },
        RESULT: False
    },
    {
        VALUE: None,
        SCHEMA: {
            'type': 'boolean',
            'default': True
        },
        RESULT: True
    },
    {
        VALUE: False,
        SCHEMA: {
            'type': 'boolean'
        },
        RESULT: False
    },
    {
        VALUE: True,
        SCHEMA: {
            'type': 'boolean'
        },
        RESULT: True
    },
]

BUILD_BOOLEAN_FAIL = [
    {
        VALUE: 'invalid',
        SCHEMA: {
            'type': 'boolean'
        }
    },
]


class ConstTest(unittest.TestCase):
    def test_build_boolean(self):
        for entry in BUILD_BOOLEAN:
            self.assertEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_boolean_fail(self):
        for entry in BUILD_BOOLEAN_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])
