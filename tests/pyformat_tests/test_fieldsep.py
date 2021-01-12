import unittest

import pyformat


STRING = 'string'
CONTEXT = 'context'
RESULT = 'result'

FORMAT_CONTEXT_FIELDSEP_STRINGS = [
    {
        STRING: '%S1',
        CONTEXT: {
            'fields': [b'this', b' ', b'is', b' ', b'a', b' ', b'test']
        },
        RESULT: 'this'
    },
    {
        STRING: '%S2 %S1 %S3 %S4?',
        CONTEXT: {
            'fields': [b'this', b' ', b'is', b' ', b'a', b' ', b'test']
        },
        RESULT: 'is this a test?'
    },
    {
        STRING: '%S4%Se2%(S-1)%(Se-3)%S3',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'test   test   a'
    },
    {
        STRING: '%(S1*3)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'this   is    a'
    },
    {
        STRING: '%(S*3)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'this   is    a'
    },
    {
        STRING: '%(S*)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'this   is    a test'
    },
    {
        STRING: '%(S*-1)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'this   is    a test'
    },
    {
        STRING: '%(S2*-2)%(Se-1)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'is    a '
    },
    {
        STRING: '%(S2*-3)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'is'
    },
    {
        STRING: '%(S3*-3)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: ''
    },
    {
        STRING: '%(Se3)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: '    '
    },
    {
        STRING: '%(Se10)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: ''
    },
    {
        STRING: '%(S1*3,+)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'this+is+a'
    }
]


class FieldsepTest(unittest.TestCase):
    def test_format_context_fieldsep_string(self):
        for entry in FORMAT_CONTEXT_FIELDSEP_STRINGS:
            self.assertEqual(
                pyformat.format_string(entry[STRING], context=entry[CONTEXT]),
                entry[RESULT]
            )
