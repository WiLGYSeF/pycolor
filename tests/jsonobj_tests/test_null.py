import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_NULL = [
    {
        VALUE: None,
        SCHEMA: {
            'type': 'null'
        },
        RESULT: None
    },
]

BUILD_NULL_FAIL = [
    {
        VALUE: 123,
        SCHEMA: {
            'type': 'null'
        }
    },
]


class NullTest(unittest.TestCase):
    def test_build_null(self):
        for entry in BUILD_NULL:
            self.assertEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_null_fail(self):
        for entry in BUILD_NULL_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])
