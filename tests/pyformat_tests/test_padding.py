import unittest

from src.pycolor import pyformat


STRING = 'string'
CONTEXT = 'context'
RESULT = 'result'

FIELDS_THIS_IS_A_TEST = ['this', '   ', 'is', '    ', 'a', ' ', 'test']

FORMAT_CONTEXT_PADDING_STRING = [
    {
        STRING: '%P%F1',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this'
    },
    {
        STRING: '%P(%F1)',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: ''
    },
    {
        STRING: '%P(2;%F1)%F1',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this'
    },
    {
        STRING: '%P(6;%F1)%F1',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: '  this'
    },
    {
        STRING: '%P(-6;%F1)%F1',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this'
    },
    {
        STRING: '%P(z;%F1)%F1',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: 'this'
    },
    {
        STRING: '%P(8,0;12345)12345',
        CONTEXT: {
            'fields': FIELDS_THIS_IS_A_TEST
        },
        RESULT: '00012345'
    },
]


class PaddingTest(unittest.TestCase):
    def test_format_context_padding_string(self):
        for entry in FORMAT_CONTEXT_PADDING_STRING:
            self.assertEqual(
                pyformat.fmt_str(entry[STRING], context=entry[CONTEXT]),
                entry[RESULT]
            )
