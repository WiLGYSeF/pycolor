import unittest

from src.pycolor import pyformat

STRING = 'string'
CONTEXT = 'context'
RESULT = 'result'

FIELDS_THIS_IS_A_TEST = ['this', '   ', 'is', '    ', 'a', ' ', 'test']

class PaddingTest(unittest.TestCase):
    def test_format_context_padding_string(self):
        entries = [
            {
                STRING: '%P%F1',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this'
            },
            {
                STRING: '%P(%F1)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: ''
            },
            {
                STRING: '%P(2;%F1)%F1',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this'
            },
            {
                STRING: '%P(6;%F1)%F1',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: '  this'
            },
            {
                STRING: '%P(-6;%F1)%F1',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this'
            },
            {
                STRING: '%P(z;%F1)%F1',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this'
            },
            {
                STRING: '%P(8,0;12345)12345',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: '00012345'
            },
        ]

        for entry in entries:
            string = entry[STRING]
            context = entry[CONTEXT]
            with self.subTest(string=string, context=context):
                self.assertEqual(
                    entry[RESULT],
                    pyformat.fmt_str(string, context=context),
                )
