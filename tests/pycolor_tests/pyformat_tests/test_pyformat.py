import unittest

from src.pycolor.pycolor import pyformat

ARGS = 'args'
VALUE = 'value'

class PyformatTest(unittest.TestCase):
    def test_get_formatter(self):
        entries = [
            {
                ARGS: '%C',
                VALUE: ('C', None)
            },
            {
                ARGS: '%Cred',
                VALUE: ('C', 'red')
            },
            {
                ARGS: '%Cred-orange',
                VALUE: ('C', 'red')
            },
            {
                ARGS: 'abc%C(red-orange)abc',
                VALUE: ('C', 'red-orange')
            },
            {
                ARGS: '%C(ab(c)d)e',
                VALUE: ('C', None)
            },
            {
                ARGS: r'%C(ab\(c)d)e',
                VALUE: ('C', None)
            },
            {
                ARGS: '%(color:red-orange)',
                VALUE: ('color', 'red-orange')
            },
        ]

        for entry in entries:
            args = entry[ARGS]
            with self.subTest(args=args):
                self.assertTupleEqual(
                    entry[VALUE],
                    pyformat.get_format_param(pyformat.FORMAT_REGEX.search(args))
                )

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
