import unittest

from src.pycolor import pyformat

STRING = 'string'
RESULT = 'result'
CONTEXT = 'context'
ALIASES = 'aliases'

class ColorTest(unittest.TestCase):
    def test_format_color_string(self):
        entries = {
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

        for key, val in entries.items():
            with self.subTest(string=key):
                self.assertEqual(val, pyformat.fmt_str(key))

    def test_format_color_string_prev(self):
        entries = [
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

        for entry in entries:
            string = entry[STRING]
            context = entry[CONTEXT]
            with self.subTest(string=string, context=context):
                self.assertEqual(entry[RESULT], pyformat.fmt_str(string, context=context))

    def test_format_color_string_soft_reset(self):
        entries = [
            {
                STRING: 'a%C(b)s%C(str;bol)d%C(soft)f',
                RESULT: 'a\x1b[34ms\x1b[9;1md\x1b[21;29;39mf',
            },
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                self.assertEqual(entry[RESULT], pyformat.fmt_str(string))

    def test_format_color_string_color_disabled(self):
        self.assertEqual('test',
            pyformat.fmt_str(
                '%C(red)test',
                context={
                    'color': {
                        'enabled': False
                    }
                }
            )
        )

    def test_format_color_string_aliases(self):
        entries = [
            {
                ALIASES: {
                    'asdf': 'red'
                },
                STRING: '%C(asdf)test',
                RESULT: '\x1b[31mtest'
            }
        ]

        for entry in entries:
            aliases = entry[ALIASES]
            string = entry[STRING]
            with self.subTest(aliases=aliases, string=string):
                self.assertEqual(
                    entry[RESULT],
                    pyformat.fmt_str(
                        string,
                        context={
                            'color': {
                                'aliases': aliases
                            }
                        }
                    )
                )

    def test_remove_ansi_color(self):
        entries = {
            'abcdef': 'abcdef',
            'a\x1b[31mbc': 'abc',
            '\x1b[1;32mh\x1b[2;35me\x1b[31mll\x1b[0mo': 'hello',
        }

        for key, val in entries.items():
            with self.subTest(string=key):
                self.assertEqual(val, pyformat.color.remove_ansi_color(key))

    def test_is_ansi_reset(self):
        entries = {
            '': False,
            'abcdef': False,
            '\x1b[0m': True,
            '\x1b[31;0m': True,
            '\x1b[0;31m': False,
            '\x1b[0;m': True,
            '\x1b[00m': True,
        }

        for key, val in entries.items():
            with self.subTest(string=key):
                self.assertEqual(val, pyformat.color.is_ansi_reset(key))

    def test_hex_to_rgb(self):
        entries = {
            '0xffffff': (255, 255, 255),
            '0xfff': (255, 255, 255),
            'ffffff': (255, 255, 255),
            'eee': (238, 238, 238),
            '0xffaa00': (255, 170, 0),
            '0xfa0': (255, 170, 0),
            'invalid': ValueError(),
            '0xbcdefg': ValueError(),
        }

        for key, val in entries.items():
            with self.subTest(string=key):
                if isinstance(val, Exception):
                    self.assertRaises(type(val), pyformat.color.hex_to_rgb, key)
                else:
                    self.assertTupleEqual(val, pyformat.color.hex_to_rgb(key))
