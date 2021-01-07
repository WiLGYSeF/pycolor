import unittest

import pyformat


ARGS = 'args'
VALUE = 'value'

GET_FORMATTER_STRINGS = [
    {
        ARGS: ('', 0),
        VALUE: (None, 0)
    },
    {
        ARGS: ('abc', 0),
        VALUE: (None, 0)
    },
    {
        ARGS: ('%Cred', 0),
        VALUE: ('Cred', 5)
    },
    {
        ARGS: ('%Cred-orange', 0),
        VALUE: ('Cred', 5)
    },
    {
        ARGS: ('abc%Cred-orange', 3),
        VALUE: ('Cred', 8)
    },
    {
        ARGS: ('abc%(Cred-orange)abc', 3),
        VALUE: ('Cred-orange', 17)
    }
]

FORMAT_STRINGS = {
    '': '',
    'abc': 'abc',
    'abc%': 'abc%',
    'abc%(Cred)abc': 'abc\x1b[31mabc',
    r'abc\%(Cred)abc': r'abc\%(Cred)abc',
    'abc\\': 'abc\\',
    '%Cinvalid': ''
}


class FormatterTest(unittest.TestCase):
    def test_get_formatter(self):
        for entry in GET_FORMATTER_STRINGS:
            self.assertTupleEqual(pyformat.get_formatter(*entry[ARGS]), entry[VALUE])

    def test_format_string(self):
        for key, val in FORMAT_STRINGS.items():
            self.assertEqual(pyformat.format_string(key), val)
