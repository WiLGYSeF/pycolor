import unittest

import pyformat


FORMAT_COLOR_STRINGS = {
    'abc%(Cred)abc': 'abc\x1b[31mabc',
    r'abc\%(Cred)abc': r'abc\%(Cred)abc',
    '%Cinvalid': '',
    '%Cred%Cblue': '\x1b[31m\x1b[34m',
    '%(Cred)%(Cblue)': '\x1b[31m\x1b[34m',
    '%(Cred;^blue)': '\x1b[31;44m',
    '%C(red)abc': '\x1b[31mabc',
    '%(Cunderline;red)abc%(C^underline)': '\x1b[4;31mabc\x1b[24m'
}


class ColorTest(unittest.TestCase):
    def test_format_color_string(self):
        for key, val in FORMAT_COLOR_STRINGS.items():
            self.assertEqual(pyformat.format_string(key), val)
