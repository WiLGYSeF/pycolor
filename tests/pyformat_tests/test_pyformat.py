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
        ARGS: ('%C', 0),
        VALUE: ('C', 2)
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
    },
    {
        ARGS: ('abc%C(red-orange)abc', 3),
        VALUE: ('Cred-orange', 17)
    }
]

FORMAT_STRINGS = {
    '': '',
    'abc': 'abc',
    'abc%': 'abc%',
    'abc\\': 'abc\\',
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
        STRING: '%Ginvalid abc %Ginvalid',
        CONTEXT: {
            'match': Match('abc 123 abc', {
                1: '123'
            })
        },
        RESULT: ' abc '
    }
]

COLORS = 'colors'
STRING = 'string'
VALUE = 'value'
GET_LASTCOLORS = [
    {
        COLORS: [],
        STRING: '',
        VALUE: ''
    },
    {
        COLORS: ['\x1b[31m'],
        STRING: '',
        VALUE: '\x1b[31m'
    },
    {
        COLORS: ['\x1b[31m'],
        STRING: '1',
        VALUE: '\x1b[31m'
    },
    {
        COLORS: ['\x1b[31m'],
        STRING: '0',
        VALUE: '\x1b[31m'
    },
    {
        COLORS: ['\x1b[31m'],
        STRING: '-1',
        VALUE: '\x1b[31m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: 'invalid',
        VALUE: '\x1b[34m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '',
        VALUE: '\x1b[34m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '1',
        VALUE: '\x1b[34m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '2',
        VALUE: '\x1b[33m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '3',
        VALUE: '\x1b[32m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '4',
        VALUE: '\x1b[31m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '5',
        VALUE: '\x1b[31m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '-1',
        VALUE: '\x1b[31m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '-2',
        VALUE: '\x1b[32m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '-3',
        VALUE: '\x1b[33m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '-4',
        VALUE: '\x1b[34m'
    },
    {
        COLORS: ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m'],
        STRING: '-5',
        VALUE: '\x1b[34m'
    },
]


class PyformatTest(unittest.TestCase):
    def test_get_formatter(self):
        for entry in GET_FORMATTER_STRINGS:
            self.assertTupleEqual(pyformat.get_formatter(*entry[ARGS]), entry[VALUE])

    def test_format_string(self):
        for key, val in FORMAT_STRINGS.items():
            self.assertEqual(pyformat.format_string(key), val)

    def test_format_context_group_string(self):
        for entry in FORMAT_CONTEXT_GROUP_STRINGS:
            self.assertEqual(
                pyformat.format_string(entry[STRING], context=entry[CONTEXT]),
                entry[RESULT]
            )

    def test_get_lastcolor(self):
        for entry in GET_LASTCOLORS:
            self.assertEqual(pyformat.get_lastcolor(entry[COLORS], entry[STRING]), entry[VALUE])
