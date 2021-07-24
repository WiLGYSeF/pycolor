import unittest

import pyformat


STRING = 'string'
RESULT = 'result'

FORMAT_TRUNCATE_STRING = [
    {
        STRING: '%T(this is a test;...;end,100)',
        RESULT: 'this is a test'
    },
    {
        STRING: '%T(this is a test;...;end,8)',
        RESULT: 'this ...'
    },
    {
        STRING: '%T(this is a test;...;start,8)',
        RESULT: '... test'
    },
    {
        STRING: '%T(this is a test;...;mid,8)',
        RESULT: 'th...est'
    },
    {
        STRING: '%T(this is a test;...;end-add,8)',
        RESULT: 'this is ...'
    },
    {
        STRING: '%T(this is a test;...;start-add,8)',
        RESULT: '...s a test'
    },
    {
        STRING: '%T(this is a test;\x1b[2\\;33m...\x1b[0m;mid-add,8)',
        RESULT: 'this\x1b[2;33m...\x1b[0mtest'
    },
    {
        STRING: '%T(this is an uneven test;...;mid-add,13)',
        RESULT: 'this i...en test'
    },
    {
        STRING: '%T(this is a test;;end,8)',
        RESULT: 'this is '
    },
    {
        STRING: '%T(this is a test;end,8)',
        RESULT: 'this is '
    },
    {
        STRING: '%T(;...;end-add,8)',
        RESULT: ''
    },
    {
        STRING: '%T(this is a test;...;invalid,8)',
        RESULT: ValueError
    },
    {
        STRING: '%T(this is a test;...;end-add,-8)',
        RESULT: ValueError
    },
    {
        STRING: '%T(this is a test;...;-8)',
        RESULT: ValueError
    },
    {
        STRING: '%T(this is a test;...;end)',
        RESULT: ValueError
    },
]


class TruncateTest(unittest.TestCase):
    def test_truncate(self):
        for entry in FORMAT_TRUNCATE_STRING:
            if isinstance(entry[RESULT], type):
                with self.assertRaises(entry[RESULT]):
                    pyformat.format_string(entry[STRING])
            else:
                self.assertEqual(
                    pyformat.format_string(entry[STRING]),
                    entry[RESULT]
                )
