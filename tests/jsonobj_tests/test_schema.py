import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_REF = [
    {
        VALUE: {
            'obj': {
                'abc': 123
            }
        },
        SCHEMA: {
            'definitions': {
                'a': {
                    'properties': {
                        'abc': {'type': 'number'},
                        'b': {'type': 'boolean', 'default': True}
                    }
                }
            },

            'type': 'object',
            'properties': {
                'obj': { '$ref': '#/definitions/a' }
            }
        },
        RESULT: {
            'obj': {
                'abc': 123,
                'b': True
            }
        }
    },
]

BUILD_REF_FAIL = [
    {
        VALUE: {
            'obj': {
                'abc': 'def'
            }
        },
        SCHEMA: {
            'definitions': {
                'a': {
                    'properties': {
                        'abc': {'type': 'number'},
                        'b': {'type': 'boolean', 'default': True}
                    }
                }
            },

            'type': 'object',
            'properties': {
                'obj': { '$ref': '#/definitions/a' }
            }
        }
    },
]


class JsonobjTest(unittest.TestCase):
    def test_build_ref(self):
        for entry in BUILD_REF:
            self.assertEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_ref_fail(self):
        for entry in BUILD_REF_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])
