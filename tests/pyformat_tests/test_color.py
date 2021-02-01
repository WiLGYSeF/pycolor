import unittest

import pyformat
import pyformat.color


FORMAT_COLOR_STRING = {
    'abc%C(red)abc': 'abc\x1b[31mabc',
    r'abc\%C(red)abc': r'abc\%C(red)abc',
    '%Cinvalid': '',
    '%Cred%Cblue': '\x1b[31m\x1b[34m',
    '%(Cred)%(Cblue)': '\x1b[31m\x1b[34m',
    '%C(red;^blue)': '\x1b[31;44m',
    '%C(red)abc': '\x1b[31mabc',
    '%C(123)abc': '\x1b[38;5;123mabc',
    '%C(0xffaa00)abc': '\x1b[38;2;255;170;0mabc',
    '%C(underline;red)abc%C(^underline)': '\x1b[4;31mabc\x1b[24m',
    '%C(und;red)abc%C(^und)': '\x1b[4;31mabc\x1b[24m',
    '%C(red)a%C(green)b%C(last)c': '\x1b[31ma\x1b[32mb\x1b[32mc',
    '%C(red)a%C(green)b%C(prev)c': '\x1b[31ma\x1b[32mb\x1b[31mc',
    '%C(raw1;4;38;5;40)abc': '\x1b[1;4;38;5;40mabc',
}

ALIASES = 'aliases'
STRING = 'string'
RESULT = 'result'

FORMAT_COLOR_STRING_ALIASES = [
    {
        ALIASES: {
            'asdf': 'red'
        },
        STRING: '%C(asdf)test',
        RESULT: '\x1b[31mtest'
    }
]

IS_ANSI_RESET = {
    '': False,
    'abcdef': False,
    '\x1b[0m': True,
    '\x1b[31;0m': True,
    '\x1b[0;31m': False,
    '\x1b[0;m': True,
    '\x1b[00m': True,
}

HEX_TO_RGB = {
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
        for key, val in FORMAT_COLOR_STRING.items():
            self.assertEqual(pyformat.format_string(key), val)

    def test_format_color_string_color_disabled(self):
        self.assertEqual(pyformat.format_string(
            '%C(red)test',
            context={
                'color_enabled': False
            }
        ), 'test')

    def test_format_color_string_aliases(self):
        for entry in FORMAT_COLOR_STRING_ALIASES:
            self.assertEqual(pyformat.format_string(
                entry[STRING],
                context={
                    'color_aliases': entry[ALIASES]
                }
            ), entry[RESULT])

    def test_is_ansi_reset(self):
        for key, val in IS_ANSI_RESET.items():
            self.assertEqual(pyformat.color.is_ansi_reset(key), val)

    def test_hex_to_rgb(self):
        for key, val in HEX_TO_RGB.items():
            if isinstance(val, Exception):
                self.assertRaises(Exception, pyformat.color.hex_to_rgb, key)
            else:
                self.assertTupleEqual(pyformat.color.hex_to_rgb(key), val)
