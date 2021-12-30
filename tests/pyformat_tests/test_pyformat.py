import unittest

from src.pycolor import pyformat

ARGS = 'args'
VALUE = 'value'

class PyformatTest(unittest.TestCase):
    def test_get_formatter(self):
        entries = [
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

        for entry in entries:
            args = entry[ARGS]
            with self.subTest(args=args):
                self.assertTupleEqual(entry[VALUE], pyformat.get_formatter(*args))

    def test_format_string(self):
        entries = {
            '': '',
            'abc': 'abc',
            'abc%': 'abc%',
            '20%% complete': '20% complete',
            'abc\\123': 'abc\\123',
        }

        for key, val in entries.items():
            with self.subTest(string=key):
                self.assertEqual(pyformat.fmt_str(key), val)
