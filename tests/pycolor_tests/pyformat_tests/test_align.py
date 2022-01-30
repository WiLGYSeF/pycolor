import unittest

from src.pycolor.pycolor.pyformat import Formatter
from src.pycolor.pycolor.pyformat.context import Context

STRING = 'string'
CONTEXT = 'context'
RESULT = 'result'

FIELDS_THIS_IS_A_TEST = ['this', '   ', 'is', '    ', 'a', ' ', 'test']

class AlignTest(unittest.TestCase):
    def test_format_context_align_string(self):
        entries = [
            {
                STRING: '%(align)%F1',
                CONTEXT: Context(fields=FIELDS_THIS_IS_A_TEST),
                RESULT: 'this'
            },
            {
                STRING: '%(align)%F1%(end)',
                CONTEXT: Context(fields=FIELDS_THIS_IS_A_TEST),
                RESULT: 'this'
            },
            {
                STRING: '%(align:2)%F1%(end)',
                CONTEXT: Context(fields=FIELDS_THIS_IS_A_TEST),
                RESULT: 'this'
            },
            {
                STRING: '%(align:6)%F1',
                CONTEXT: Context(fields=FIELDS_THIS_IS_A_TEST),
                RESULT: 'this  '
            },
            {
                STRING: '%(align:-6)%F1%(end)',
                CONTEXT: Context(fields=FIELDS_THIS_IS_A_TEST),
                RESULT: 'this'
            },
            {
                STRING: '%(align:6:z)%F1',
                CONTEXT: Context(fields=FIELDS_THIS_IS_A_TEST),
                RESULT: 'this'
            },
            {
                STRING: '%(align:6,z)%F1%(end)',
                CONTEXT: Context(fields=FIELDS_THIS_IS_A_TEST),
                RESULT: 'this  '
            },
            {
                STRING: '=%(align:8,left,0)12345%(end)=',
                CONTEXT: Context(fields=FIELDS_THIS_IS_A_TEST),
                RESULT: '=12345000='
            },
            {
                STRING: '%(align:8,middle,0)12345%(end)',
                CONTEXT: Context(fields=FIELDS_THIS_IS_A_TEST),
                RESULT: '01234500'
            },
            {
                STRING: '%(align:8,right,0)12345%(end)',
                CONTEXT: Context(fields=FIELDS_THIS_IS_A_TEST),
                RESULT: '00012345'
            },
        ]

        for entry in entries:
            string = entry[STRING]
            context = entry[CONTEXT]
            with self.subTest(string=string, context=context):
                formatter = Formatter(context=context)
                self.assertEqual(entry[RESULT], formatter.fmt_str(string))
