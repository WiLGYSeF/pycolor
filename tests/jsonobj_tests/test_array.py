import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_ARRAY = [
    {
        VALUE: None,
        SCHEMA: {
            'type': 'array'
        },
        RESULT: []
    },
    {
        VALUE: ['abc', 123.45],
        SCHEMA: {
            'type': 'array'
        },
        RESULT: ['abc', 123.45]
    },
    {
        VALUE: ['abc', 123.45],
        SCHEMA: {
            'type': 'array',
            'minItems': 1
        },
        RESULT: ['abc', 123.45]
    },
    {
        VALUE: ['abc', 123.45],
        SCHEMA: {
            'type': 'array',
            'maxItems': 3
        },
        RESULT: ['abc', 123.45]
    },
    {
        VALUE: [7, 123.45],
        SCHEMA: {
            'type': 'array',
            'items': {
                'type': 'number'
            }
        },
        RESULT: [7, 123.45]
    },
    {
        VALUE: [7, 'abc'],
        SCHEMA: {
            'type': 'array',
            'items': [
                {
                    'type': 'number'
                },
                {
                    'type': 'string'
                },
            ]
        },
        RESULT: [7, 'abc']
    },
    {
        VALUE: [7, 'abc', True],
        SCHEMA: {
            'type': 'array',
            'items': [
                {
                    'type': 'number'
                },
                {
                    'type': 'string'
                },
            ],
            'additionalItems': True
        },
        RESULT: [7, 'abc', True]
    },
    {
        VALUE: [7, 'abc', True],
        SCHEMA: {
            'type': 'array',
            'items': [
                {
                    'type': 'number'
                },
                {
                    'type': 'string'
                },
            ],
            'additionalItems': {
                'type': 'boolean'
            }
        },
        RESULT: [7, 'abc', True]
    },
    {
        VALUE: [7, 'abc', True],
        SCHEMA: {
            'type': 'array',
            'contains': {
                'type': 'string'
            }
        },
        RESULT: [7, 'abc', True]
    },
    {
        VALUE: ['abc', 123.45],
        SCHEMA: {
            'type': 'array',
            'uniqueItems': True
        },
        RESULT: ['abc', 123.45]
    },
]

BUILD_ARRAY_FAIL = [
    {
        VALUE: 'abc',
        SCHEMA: {
            'type': 'array'
        }
    },
    {
        VALUE: ['abc', 123.45],
        SCHEMA: {
            'type': 'array',
            'minItems': 3
        }
    },
    {
        VALUE: ['abc', 123.45],
        SCHEMA: {
            'type': 'array',
            'maxItems': 1
        }
    },
    {
        VALUE: ['abc', 123.45],
        SCHEMA: {
            'type': 'array',
            'items': {
                'type': 'number'
            }
        }
    },
    {
        VALUE: [7, 123.45],
        SCHEMA: {
            'type': 'array',
            'items': {
                'type': 'number',
                'minimum': 10
            }
        }
    },
    {
        VALUE: [7, 852],
        SCHEMA: {
            'type': 'array',
            'items': [
                {
                    'type': 'number'
                },
                {
                    'type': 'string'
                },
            ]
        }
    },
    {
        VALUE: [7],
        SCHEMA: {
            'type': 'array',
            'items': [
                {
                    'type': 'number'
                },
                {
                    'type': 'string'
                },
            ]
        },
    },
    {
        VALUE: [7, 'abc', True],
        SCHEMA: {
            'type': 'array',
            'items': [
                {
                    'type': 'number'
                },
                {
                    'type': 'string'
                },
            ],
            'additionalItems': False
        }
    },
    {
        VALUE: [7, 'abc', 3],
        SCHEMA: {
            'type': 'array',
            'items': [
                {
                    'type': 'number'
                },
                {
                    'type': 'string'
                },
            ],
            'additionalItems': {
                'type': 'boolean'
            }
        }
    },
    {
        VALUE: [7, 'abc', True],
        SCHEMA: {
            'type': 'array',
            'contains': {
                'type': 'null'
            }
        }
    },
    {
        VALUE: ['abc', 'abc'],
        SCHEMA: {
            'type': 'array',
            'uniqueItems': True
        }
    },
]


class ArrayTest(unittest.TestCase):
    def test_build_number(self):
        for entry in BUILD_ARRAY:
            self.assertListEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_number_fail(self):
        for entry in BUILD_ARRAY_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])
