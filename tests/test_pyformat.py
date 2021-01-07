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
    'abc%': 'abc%'
}

FORMAT_COLOR_STRINGS = {
    'abc%(Cred)abc': 'abc\x1b[31mabc',
    r'abc\%(Cred)abc': r'abc\%(Cred)abc',
    'abc\\': 'abc\\',
    '%Cinvalid': '',
    '%Cred%Cblue': '\x1b[31m\x1b[34m',
    '%(Cred)%(Cblue)': '\x1b[31m\x1b[34m',
    '%(Cred;^blue)': '\x1b[31;44m',
    '%(Cunderline;red)abc%(C^underline)': '\x1b[4;31mabc\x1b[24m'
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

FORMAT_CONTEXT_FIELDSEP_STRINGS = [
    {
        STRING: '%S1',
        CONTEXT: {
            'fields': [b'this', b' ', b'is', b' ', b'a', b' ', b'test']
        },
        RESULT: 'this'
    },
    {
        STRING: '%S2 %S1 %S3 %S4?',
        CONTEXT: {
            'fields': [b'this', b' ', b'is', b' ', b'a', b' ', b'test']
        },
        RESULT: 'is this a test?'
    },
    {
        STRING: '%S4%Se2%(S-1)%(Se-3)%S3',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'test   test   a'
    },
    {
        STRING: '%(S1*3)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'this   is    a'
    },
    {
        STRING: '%(S*3)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'this   is    a'
    },
    {
        STRING: '%(S*)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'this   is    a test'
    },
    {
        STRING: '%(S*-1)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'this   is    a test'
    },
    {
        STRING: '%(S2*-2)%(Se-1)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'is    a '
    },
    {
        STRING: '%(S2*-3)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'is'
    },
    {
        STRING: '%(S3*-3)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: ''
    },
    {
        STRING: '%(Se3)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: '    '
    },
    {
        STRING: '%(Se10)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: ''
    },
    {
        STRING: '%(S1*3,+)',
        CONTEXT: {
            'fields': [b'this', b'   ', b'is', b'    ', b'a', b' ', b'test']
        },
        RESULT: 'this+is+a'
    },
]


class FormatterTest(unittest.TestCase):
    def test_get_formatter(self):
        for entry in GET_FORMATTER_STRINGS:
            self.assertTupleEqual(pyformat.get_formatter(*entry[ARGS]), entry[VALUE])

    def test_format_string(self):
        for key, val in FORMAT_STRINGS.items():
            self.assertEqual(pyformat.format_string(key), val)

    def test_format_color_string(self):
        for key, val in FORMAT_COLOR_STRINGS.items():
            self.assertEqual(pyformat.format_string(key), val)

    def test_format_context_group_string(self):
        for entry in FORMAT_CONTEXT_GROUP_STRINGS:
            self.assertEqual(
                pyformat.format_string(entry[STRING], context=entry[CONTEXT]),
                entry[RESULT]
            )

    def test_format_context_fieldsep_string(self):
        for entry in FORMAT_CONTEXT_FIELDSEP_STRINGS:
            self.assertEqual(
                pyformat.format_string(entry[STRING], context=entry[CONTEXT]),
                entry[RESULT]
            )
