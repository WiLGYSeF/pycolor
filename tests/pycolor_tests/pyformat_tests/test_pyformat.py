import unittest

from src.pycolor.pycolor import pyformat

STRING = 'string'
RESULT = 'result'

class PyformatTest(unittest.TestCase):
    def test_get_formatter(self):
        entries = [
            {
                STRING: '%C',
                RESULT: ('C', None)
            },
            {
                STRING: '%Cred',
                RESULT: ('C', 'red')
            },
            {
                STRING: '%Cred-orange',
                RESULT: ('C', 'red')
            },
            {
                STRING: 'abc%C(red-orange)abc',
                RESULT: ('C', 'red-orange')
            },
            {
                STRING: '%C(ab(c)d)e',
                RESULT: ('C', None)
            },
            {
                STRING: r'%C(ab\(c)d)e',
                RESULT: ('C', None)
            },
            {
                STRING: '%(color:red-orange)',
                RESULT: ('color', 'red-orange')
            },
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                self.assertTupleEqual(
                    entry[RESULT],
                    pyformat.get_format_param(pyformat.FORMAT_REGEX.search(string))
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
                self.assertEqual(val, pyformat.fmt_str(key))

    def test_format_nested_formats(self):
        entries = [
            {
                STRING: '|%(align:12,right)=%(trunc:7,middle,##)0123456789%(end)=%(end)|',
                RESULT: '|   =01##789=|'
            }
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                self.assertEqual(entry[RESULT], pyformat.fmt_str(string))
