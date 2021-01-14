import unittest

import pyformat
import pyformat.color


FORMAT_COLOR_STRINGS = {
    'abc%(Cred)abc': 'abc\x1b[31mabc',
    r'abc\%(Cred)abc': r'abc\%(Cred)abc',
    '%Cinvalid': '',
    '%Cred%Cblue': '\x1b[31m\x1b[34m',
    '%(Cred)%(Cblue)': '\x1b[31m\x1b[34m',
    '%(Cred;^blue)': '\x1b[31;44m',
    '%C(red)abc': '\x1b[31mabc',
    '%(C123)abc': '\x1b[38;5;123mabc',
    '%(C0xffaa00)abc': '\x1b[38;2;255;170;0mabc',
    '%(Cunderline;red)abc%(C^underline)': '\x1b[4;31mabc\x1b[24m'
}

HEX_TO_RGBS = {
    '0xffffff': (255, 255, 255),
    '0xfff': (255, 255, 255),
    'ffffff': (255, 255, 255),
    'fff': (255, 255, 255),
    '0xffaa00': (255, 170, 0),
    '0xfa0': (255, 170, 0),
    'invalid': ValueError()
}


class ColorTest(unittest.TestCase):
    def test_format_color_string(self):
        for key, val in FORMAT_COLOR_STRINGS.items():
            self.assertEqual(pyformat.format_string(key), val)

    def test_hex_to_rgb(self):
        for key, val in HEX_TO_RGBS.items():
            if isinstance(val, Exception):
                self.assertRaises(Exception, pyformat.color.hex_to_rgb, key)
            else:
                self.assertTupleEqual(pyformat.color.hex_to_rgb(key), val)
