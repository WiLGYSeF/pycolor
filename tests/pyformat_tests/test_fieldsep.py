import unittest

from src.pycolor import pyformat


STRING = 'string'
CONTEXT = 'context'
FIELD = 'field'
RESULT = 'result'

FIELDS_THIS_IS_A_TEST = ['this', '   ', 'is', '    ', 'a', ' ', 'test']

class FieldsepTest(unittest.TestCase):
    def test_format_context_fieldsep_string(self):
        entries = [
            {
                STRING: '%F1',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this'
            },
            {
                STRING: '%F2 %F1 %F3 %F4?',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'is this a test?'
            },
            {
                STRING: '%F4%Fs2%F(-1)%F(s-3)%F3',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'test   test   a'
            },
            {
                STRING: '%F(s3)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: '    '
            },
            {
                STRING: '%F(s10)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: ''
            },
        ]

        for entry in entries:
            string = entry[STRING]
            context = entry[CONTEXT]
            with self.subTest(string=string, context=context):
                self.assertEqual(
                    entry[RESULT],
                    pyformat.fmt_str(entry[STRING], context=entry[CONTEXT])
                )

    def test_format_context_fieldsep_string_range(self):
        entries = [
            {
                STRING: '%F(1*3)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this   is    a'
            },
            {
                STRING: '%F(*3)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this   is    a'
            },
            {
                STRING: '%F(*)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this   is    a test'
            },
            {
                STRING: '%F(*-1)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this   is    a test'
            },
            {
                STRING: '%F(2*-2)%F(s-1)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'is    a '
            },
            {
                STRING: '%F(2*-3)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'is'
            },
            {
                STRING: '%F(3*-3)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: ''
            },
        ]

        for entry in entries:
            string = entry[STRING]
            context = entry[CONTEXT]
            with self.subTest(string=string, context=context):
                self.assertEqual(
                    entry[RESULT],
                    pyformat.fmt_str(entry[STRING], context=entry[CONTEXT])
                )

    def test_format_context_fieldsep_string_range_replace(self):
        entries = [
            {
                STRING: '%F(1*3,+)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this+is+a'
            },
            {
                STRING: '%F(1*8,+)',
                CONTEXT: {'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: 'this+is+a+test'
            },
            {
                STRING: '%F(7*10,+)',
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: ''
            },
        ]

        for entry in entries:
            string = entry[STRING]
            context = entry[CONTEXT]
            with self.subTest(string=string, context=context):
                self.assertEqual(
                    entry[RESULT],
                    pyformat.fmt_str(entry[STRING], context=entry[CONTEXT])
                )

    def test_format_context_fieldsep_color(self):
        entries = [
            {
                STRING: '%F1 %Hb',
                CONTEXT: {
                    'field_cur': 'test',
                    'fields': FIELDS_THIS_IS_A_TEST
                },
                RESULT: 'this \x1b[34mtest\x1b[0m'
            }
        ]

        for entry in entries:
            string = entry[STRING]
            context = entry[CONTEXT]
            with self.subTest(string=string, context=context):
                self.assertEqual(
                    entry[RESULT],
                    pyformat.fmt_str(entry[STRING], context=entry[CONTEXT])
                )

    def test_get_join_field(self):
        entries = [
            {
                FIELD: -2,
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: '    '
            },
            {
                FIELD: 0,
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: ''
            },
            {
                FIELD: 1,
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: ''
            },
            {
                FIELD: 2,
                CONTEXT: { 'fields': FIELDS_THIS_IS_A_TEST },
                RESULT: '   '
            },
        ]

        for entry in entries:
            field = entry[FIELD]
            context = entry[CONTEXT]
            with self.subTest(field=field, context=context):
                self.assertEqual(
                    entry[RESULT],
                    pyformat.fieldsep.get_join_field(field, context['fields'])
                )
