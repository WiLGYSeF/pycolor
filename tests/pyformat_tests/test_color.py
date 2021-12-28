import unittest

from src.pycolor import pyformat


STRING = 'string'
RESULT = 'result'

FORMAT_COLOR_STRING = {
    'abc%C(red)abc': 'abc\x1b[31mabc',
    'abc%%C(red)abc': 'abc%C(red)abc',
    '%Cinvalid': '',
    '%C': '',
    '%Cred%Cblue': '\x1b[31m\x1b[34m',
    '%C(red)%C(blue)': '\x1b[31m\x1b[34m',
    '%(Cred)%(Cblue)': '%(Cred)%(Cblue)',
    '%C(red;^blue)': '\x1b[31;44m',
    '%C(red)abc': '\x1b[31mabc',
    '%C(123)abc': '\x1b[38;5;123mabc',
    '%C(0xffaa00)abc': '\x1b[38;2;255;170;0mabc',
    '%C(underline;red)abc%C(^underline)': '\x1b[4;31mabc\x1b[24m',
    '%C(und;red)abc%C(^und)': '\x1b[4;31mabc\x1b[24m',
    '%C(raw1;4;38;5;40)abc': '\x1b[1;4;38;5;40mabc',
    '%C(overline)abc': '\x1b[53mabc',
    '%C(^overline)abc': '\x1b[55mabc',
    '%C(red': '%C(red',
    '%CC(red)': '%CC(red)',
    '%Cr)w': '\x1b[31m)w'
}

CONTEXT = 'context'
FORMAT_COLOR_STRING_PREV = [
    {
        CONTEXT: {
            'string': 'a',
            'idx': 1,
            'color': {
                'positions': {
                    0: '\x1b[31m'
                }
            }
        },
        STRING: '%C(green)b%C(prev)c',
        RESULT: '\x1b[32mb\x1b[31mc',
    },
    {
        CONTEXT: {
            'string': '',
            'idx': 0,
            'color': {
                'positions': {
                    0: '\x1b[31m'
                }
            }
        },
        STRING: '%C(green)b%C(prev)c',
        RESULT: '\x1b[32mb\x1b[31mc',
    },
]

FORMAT_COLOR_STRING_SOFT_RESET = [
    {
        STRING: 'a%C(b)s%C(str;bol)d%C(soft)f',
        RESULT: 'a\x1b[34ms\x1b[9;1md\x1b[21;29;39mf',
    },
]

ALIASES = 'aliases'
FORMAT_COLOR_STRING_ALIASES = [
    {
        ALIASES: {
            'asdf': 'red'
        },
        STRING: '%C(asdf)test',
        RESULT: '\x1b[31mtest'
    }
]

REMOVE_ANSI_COLOR = {
    'abcdef': 'abcdef',
    'a\x1b[31mbc': 'abc',
    '\x1b[1;32mh\x1b[2;35me\x1b[31mll\x1b[0mo': 'hello',
}

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
    'invalid': ValueError,
    '0xbcdefg': ValueError,
}


class ColorTest(unittest.TestCase):
    def test_format_color_string(self):
        for key, val in FORMAT_COLOR_STRING.items():
            self.assertEqual(pyformat.fmt_str(key), val)

    def test_format_color_string_prev(self):
        for entry in FORMAT_COLOR_STRING_PREV:
            self.assertEqual(pyformat.fmt_str(
                entry[STRING],
                context=entry[CONTEXT]
            ), entry[RESULT])

    def test_format_color_string_soft_reset(self):
        for entry in FORMAT_COLOR_STRING_SOFT_RESET:
            self.assertEqual(pyformat.fmt_str(
                entry[STRING],
            ), entry[RESULT])

    def test_format_color_string_color_disabled(self):
        self.assertEqual(pyformat.fmt_str(
            '%C(red)test',
            context={
                'color': {
                    'enabled': False
                }
            }
        ), 'test')

    def test_format_color_string_aliases(self):
        for entry in FORMAT_COLOR_STRING_ALIASES:
            self.assertEqual(pyformat.fmt_str(
                entry[STRING],
                context={
                    'color': {
                        'aliases': entry[ALIASES]
                    }
                }
            ), entry[RESULT])

    def test_remove_ansi_color(self):
        for key, val in REMOVE_ANSI_COLOR.items():
            self.assertEqual(pyformat.color.remove_ansi_color(key), val)

    def test_is_ansi_reset(self):
        for key, val in IS_ANSI_RESET.items():
            self.assertEqual(pyformat.color.is_ansi_reset(key), val)

    def test_hex_to_rgb(self):
        for key, val in HEX_TO_RGB.items():
            if isinstance(val, type):
                self.assertRaises(val, pyformat.color.hex_to_rgb, key)
            else:
                self.assertTupleEqual(pyformat.color.hex_to_rgb(key), val)
