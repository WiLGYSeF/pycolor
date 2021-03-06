import unittest

import pyformat


STRING = 'string'
CONTEXT = 'context'
RESULT = 'result'

FIELDS_THIS_IS_A_TEST = ['this', '   ', 'is', '    ', 'a', ' ', 'test']

FORMAT_CONTEXT_FIELDSEP_STRING = [
    {
        STRING: '%F1',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this'
    },
    {
        STRING: '%F2 %F1 %F3 %F4?',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'is this a test?'
    },
    {
        STRING: '%F4%Fs2%(F-1)%(Fs-3)%F3',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'test   test   a'
    },
    {
        STRING: '%(F1*3)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this   is    a'
    },
    {
        STRING: '%(F*3)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this   is    a'
    },
    {
        STRING: '%(F*)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this   is    a test'
    },
    {
        STRING: '%(F*-1)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this   is    a test'
    },
    {
        STRING: '%(F2*-2)%(Fs-1)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'is    a '
    },
    {
        STRING: '%(F2*-3)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'is'
    },
    {
        STRING: '%(F3*-3)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: ''
    },
    {
        STRING: '%(Fs3)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: '    '
    },
    {
        STRING: '%(Fs10)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: ''
    },
    {
        STRING: '%(F1*3,+)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this+is+a'
    },
    {
        STRING: '%(F1*8,+)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this+is+a+test'
    },
    {
        STRING: '%(F7*10,+)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: ''
    }
]

FIELD = 'field'

GET_JOIN_FIELD = [
    {
        FIELD: -2,
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: '    '
    },
    {
        FIELD: 0,
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: ''
    },
    {
        FIELD: 1,
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: ''
    },
    {
        FIELD: 2,
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: '   '
    },
]


class FieldsepTest(unittest.TestCase):
    def test_format_context_fieldsep_string(self):
        for entry in FORMAT_CONTEXT_FIELDSEP_STRING:
            self.assertEqual(
                pyformat.format_string(entry[STRING], context=entry[CONTEXT]),
                entry[RESULT]
            )

    def test_get_join_field(self):
        for entry in GET_JOIN_FIELD:
            self.assertEqual(
                pyformat.fieldsep.get_join_field(entry[FIELD], entry[CONTEXT]),
                entry[RESULT]
            )
