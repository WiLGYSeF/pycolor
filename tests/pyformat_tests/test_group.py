import unittest

import pyformat


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

FORMAT_CONTEXT_GROUP_STRINGS = [
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

FORMAT_CONTEXT_GROUP_COLOR = [
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


class GroupTest(unittest.TestCase):
    def test_format_context_group_string(self):
        for entry in FORMAT_CONTEXT_GROUP_STRINGS:
            self.assertEqual(
                pyformat.format_string(entry[STRING], context=entry[CONTEXT]),
                entry[RESULT]
            )

    def test_format_context_group_color(self):
        for entry in FORMAT_CONTEXT_GROUP_COLOR:
            context = entry[CONTEXT]
            context['match_cur'] = context['match'][1]

            self.assertEqual(
                pyformat.format_string(entry[STRING], context=context),
                entry[RESULT]
            )
