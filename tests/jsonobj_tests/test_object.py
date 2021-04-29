import unittest

import jsonobj


VALUE = 'value'
SCHEMA = 'schema'
RESULT = 'result'

BUILD_OBJECT = [
    {
        VALUE: None,
        SCHEMA: {
            'type': 'object'
        },
        RESULT: {}
    },
    {
        VALUE: {
            'abc': 123,
            'd': [True, 0.231]
        },
        SCHEMA: {
            'type': 'object',
            'minProperties': 2
        },
        RESULT: {
            'abc': 123,
            'd': [True, 0.231]
        }
    },
    {
        VALUE: {
            'abc': 123,
            'd': [True, 0.231]
        },
        SCHEMA: {
            'type': 'object',
            'maxProperties': 3
        },
        RESULT: {
            'abc': 123,
            'd': [True, 0.231]
        }
    },
    {
        VALUE: {
            'test': 'asdf',
            'custom': 3574
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'},
                'extra': {'type': 'number'}
            }
        },
        RESULT: {
            'test': 'asdf',
            'extra': 0,
            'custom': 3574
        }
    },
    {
        VALUE: {
            'test': 'asdf',
            'custom': 3574
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'}
            },
            'additionalProperties': {
                'type': 'integer'
            }
        },
        RESULT: {
            'test': 'asdf',
            'custom': 3574
        }
    },
    {
        VALUE: {
            'test': 'asdf',
            'extra': 3574
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'},
                'extra': {'type': 'number'}
            },
            'required': ['extra']
        },
        RESULT: {
            'test': 'asdf',
            'extra': 3574
        }
    },
    {
        VALUE: {
            'test': 'asdf',
            'extra': 3574
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'},
                'extra': {'type': 'number'}
            },
            'dependencies': {
                'extra': ['test']
            }
        },
        RESULT: {
            'test': 'asdf',
            'extra': 3574
        }
    },
    {
        VALUE: {},
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'},
                'extra': {'type': 'number'}
            },
            'dependencies': {
                'extra': ['test']
            }
        },
        RESULT: {
            'test': '',
            'extra': 0
        }
    },
    {
        VALUE: {
            'extra': 42.1,
            'extra2': 'abc'
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'},
                'extra': {'type': 'number'}
            },
            'dependencies': {
                'extra': {
                    'properties': {
                        'extra2': {'type': 'string'}
                    },
                    'required': ['extra2']
                }
            }
        },
        RESULT: {
            'test': '',
            'extra': 42.1,
            'extra2': 'abc'
        }
    },
    {
        VALUE: {
            'extra': 42.1
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'},
                'extra': {'type': 'number'}
            },
            'dependencies': {
                'extra': {
                    'properties': {
                        'extra2': {'type': 'string', 'default': 'def'}
                    }
                }
            }
        },
        RESULT: {
            'test': '',
            'extra': 42.1,
            'extra2': 'def'
        }
    },
]

BUILD_OBJECT_FAIL = [
    {
        VALUE: 1234,
        SCHEMA: {
            'type': 'object'
        }
    },
    {
        VALUE: {
            'abc': 123,
        },
        SCHEMA: {
            'type': 'object',
            'minProperties': 2
        }
    },
    {
        VALUE: {
            'abc': 123,
            'd': [True, 0.231],
            'ttj': '315s',
            '864': {
                'e': None
            }
        },
        SCHEMA: {
            'type': 'object',
            'maxProperties': 3
        }
    },
    {
        VALUE: {
            'test': 4,
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'}
            }
        }
    },
    {
        VALUE: {
            'test': 'asdf',
            'custom': 3574
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'}
            },
            'additionalProperties': False
        }
    },
    {
        VALUE: {
            'test': 'asdf',
            'custom': []
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'}
            },
            'additionalProperties': {
                'type': 'integer'
            }
        }
    },
    {
        VALUE: {
            'test': 'asdf'
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'},
                'extra': {'type': 'number'}
            },
            'required': ['extra']
        }
    },
    {
        VALUE: {
            'extra': 3574
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'},
                'extra': {'type': 'number'}
            },
            'dependencies': {
                'extra': ['test']
            }
        }
    },
    {
        VALUE: {
            'extra': 42.1
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'},
                'extra': {'type': 'number'}
            },
            'dependencies': {
                'extra': {
                    'properties': {
                        'extra2': {'type': 'string'}
                    },
                    'required': ['extra2']
                }
            }
        }
    },
    {
        VALUE: {
            'extra': 42.1,
            'extra2': False
        },
        SCHEMA: {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'},
                'extra': {'type': 'number'}
            },
            'dependencies': {
                'extra': {
                    'properties': {
                        'extra2': {'type': 'string'}
                    },
                    'required': ['extra2']
                }
            }
        }
    },
]


class ObjectTest(unittest.TestCase):
    def test_build_object(self):
        for entry in BUILD_OBJECT:
            self.assertEqual(
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA]),
                entry[RESULT]
            )

    def test_build_object_fail(self):
        for entry in BUILD_OBJECT_FAIL:
            with self.assertRaises(jsonobj.ValidationError):
                jsonobj.build(entry[VALUE], schema=entry[SCHEMA])
