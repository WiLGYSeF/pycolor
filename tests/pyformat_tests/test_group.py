import unittest

from src.pycolor import pyformat


class Match:
    def __init__(self, string, groupdict):
        self.string = string
        self._groupdict = groupdict

    def __getitem__(self, group):
        if group not in self._groupdict:
            raise IndexError()
        return self._groupdict[group]

STRING = 'string'
CONTEXT = 'context'
RESULT = 'result'

class GroupTest(unittest.TestCase):
    def test_format_context_group_string(self):
        entries = [
            {
                STRING: '%G1 abc %G1',
                CONTEXT: {
                    'match': Match('abc 123 abc', {
                        1: '123'
                    })
                },
                RESULT: '123 abc 123'
            },
            {
                STRING: '%ZZZ',
                CONTEXT: {},
                RESULT: '%ZZZ'
            },
            {
                STRING: '%Gname abc %Gname',
                CONTEXT: {
                    'match': Match('abc 123 abc', {
                        1: '123',
                        'name': '123'
                    })
                },
                RESULT: '123 abc 123'
            },
            {
                STRING: '%Gname abc %Gname',
                CONTEXT: {
                    'match': Match(' 123 ', {
                        1: None,
                        'name': None
                    })
                },
                RESULT: ' abc '
            },
            {
                STRING: '%Ginvalid abc %Ginvalid',
                CONTEXT: {
                    'match': Match('abc 123 abc', {
                        1: '123'
                    })
                },
                RESULT: ' abc '
            },
            {
                STRING: '%Gn abc %Gn',
                CONTEXT: {
                    'match': Match('123 abc 456', {
                        1: '123',
                        2: '456'
                    })
                },
                RESULT: '123 abc 456'
            },
            {
                STRING: '%G1 abc %G2',
                CONTEXT: {
                    'match': Match('123 abc 456', {
                        1: '123',
                        2: '456'
                    })
                },
                RESULT: '123 abc 456'
            },
            {
                STRING: '%G2 %Gn',
                CONTEXT: {
                    'match': Match('123 abc 456', {
                        1: '123',
                        2: 'abc',
                        3: '456'
                    })
                },
                RESULT: 'abc 456'
            },
            {
                STRING: '%G2 %Gn %Gn',
                CONTEXT: {
                    'match': Match('123 abc 456', {
                        1: '123',
                        2: 'abc',
                        3: '456'
                    })
                },
                RESULT: 'abc 456 '
            },
        ]

        for entry in entries:
            string = entry[STRING]
            context = entry[CONTEXT]
            with self.subTest(string=string, context=context):
                self.assertEqual(
                    entry[RESULT],
                    pyformat.fmt_str(string, context=context)
                )

    def test_format_context_group_color(self):
        entries = [
            {
                STRING: '[%Hg]',
                CONTEXT: {
                    'match': Match('abc', {
                        1: 'abc'
                    })
                },
                RESULT: '[\x1b[32mabc\x1b[0m]'
            },
            {
                STRING: '[%H(bol;r)]',
                CONTEXT: {
                    'match': Match('abc', {
                        1: 'abc'
                    })
                },
                RESULT: '[\x1b[1;31mabc\x1b[0m]'
            },
        ]

        for entry in entries:
            string = entry[STRING]
            context = entry[CONTEXT]
            context['match_cur'] = context['match'][1]

            with self.subTest(string=string, context=context):
                self.assertEqual(
                    entry[RESULT],
                    pyformat.fmt_str(string, context=context)
                )
