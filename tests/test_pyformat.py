import unittest

import pyformat


ARGS = 'args'
VALUE = 'value'

GET_FORMATTER_STRINGS = [
    {
        ARGS: ('', 0),
        VALUE: (None, 0)
    },
    {
        ARGS: ('abc', 0),
        VALUE: (None, 0)
    },
    {
        ARGS: ('%Cred', 0),
        VALUE: ('Cred', 5)
    },
    {
        ARGS: ('%Cred-orange', 0),
        VALUE: ('Cred', 5)
    },
    {
        ARGS: ('abc%Cred-orange', 3),
        VALUE: ('Cred', 8)
    },
    {
        ARGS: ('abc%(Cred-orange)abc', 3),
        VALUE: ('Cred-orange', 17)
    }
]

FORMAT_STRINGS = {
    '': '',
    'abc': 'abc',
    'abc%': 'abc%',
    'abc%(Cred)abc': 'abc\x1b[31mabc',
    r'abc\%(Cred)abc': r'abc\%(Cred)abc',
    'abc\\': 'abc\\',
    '%Cinvalid': '',
    '%Cred%Cblue': '\x1b[31m\x1b[34m',
    '%(Cred)%(Cblue)': '\x1b[31m\x1b[34m',
}

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
FORMAT_STRINGS_CONTEXT = [
    {
        STRING: '%G1 abc %G1',
        CONTEXT: {
            'match': Match(b'abc 123 abc', {
                1: b'123'
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
            'match': Match(b'abc 123 abc', {
                1: b'123',
                'name': b'123'
            })
        },
        RESULT: '123 abc 123'
    },
    {
        STRING: '%Ginvalid abc %Ginvalid',
        CONTEXT: {
            'match': Match(b'abc 123 abc', {
                1: b'123'
            })
        },
        RESULT: ' abc '
    }
]


class FormatterTest(unittest.TestCase):
    def test_get_formatter(self):
        for entry in GET_FORMATTER_STRINGS:
            self.assertTupleEqual(pyformat.get_formatter(*entry[ARGS]), entry[VALUE])

    def test_format_string(self):
        for key, val in FORMAT_STRINGS.items():
            self.assertEqual(pyformat.format_string(key), val)

    def test_format_string_context(self):
        for entry in FORMAT_STRINGS_CONTEXT:
            self.assertEqual(pyformat.format_string(
                entry[STRING],
                context=entry[CONTEXT])
            , entry[RESULT])
