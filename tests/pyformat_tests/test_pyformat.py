import unittest

from src.pycolor import pyformat


ARGS = 'args'
VALUE = 'value'

GET_FORMATTER_STRINGS = [
    {
        ARGS: ('', 0),
        VALUE: (None, None, 0)
    },
    {
        ARGS: ('abc', 0),
        VALUE: (None, None, 0)
    },
    {
        ARGS: ('%', 0),
        VALUE: (None, None, 0)
    },
    {
        ARGS: ('%C', 0),
        VALUE: ('C', '', 2)
    },
    {
        ARGS: ('%Cred', 0),
        VALUE: ('C', 'red', 5)
    },
    {
        ARGS: ('%Cred-orange', 0),
        VALUE: ('C', 'red', 5)
    },
    {
        ARGS: ('abc%Cred-orange', 3),
        VALUE: ('C', 'red', 8)
    },
    {
        ARGS: ('abc%C(red-orange)abc', 3),
        VALUE: ('C', 'red-orange', 17)
    },
    {
        ARGS: ('%C(ab(c)d)e', 0),
        VALUE: ('C', 'ab(c)d', 10)
    },
    {
        ARGS: (r'%C(ab\(c)d)e', 0),
        VALUE: ('C', r'ab\(c', 9)
    }
]

FORMAT_STRINGS = {
    '': '',
    'abc': 'abc',
    'abc%': 'abc%',
    '20%% complete': '20% complete',
    'abc\\123': 'abc\\123',
}


class PyformatTest(unittest.TestCase):
    def test_get_formatter(self):
        for entry in GET_FORMATTER_STRINGS:
            self.assertTupleEqual(pyformat.get_formatter(*entry[ARGS]), entry[VALUE])

    def test_format_string(self):
        for key, val in FORMAT_STRINGS.items():
            self.assertEqual(pyformat.format_string(key), val)
