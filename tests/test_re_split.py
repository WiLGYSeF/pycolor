import re
import unittest

from split import re_split


SEP = 'sep'
STRING = 'string'
RESULT = 'result'

RE_SPLIT_RESULTS = [
    {
        SEP: None,
        STRING: 'this is a test',
        RESULT: ['this is a test']
    },
    {
        SEP: ' ',
        STRING: 'this is a test',
        RESULT: [
            'this', ' ', 'is', ' ', 'a', ' ', 'test'
        ]
    },
    {
        SEP: ' +',
        STRING: 'this   is    a test',
        RESULT: [
            'this', '   ', 'is', '    ', 'a', ' ', 'test'
        ]
    },
    {
        SEP: ' ',
        STRING: 'this   is    a test',
        RESULT: [
            'this', ' ', '', ' ', '', ' ', 'is', ' ', '', ' ', '', ' ', '', ' ', 'a', ' ', 'test'
        ]
    },
    {
        SEP: re.compile('[-=]'),
        STRING: 'y-e=e-t',
        RESULT: [
            'y', '-', 'e', '=', 'e', '-', 't'
        ]
    }
]


class SplitTest(unittest.TestCase):
    def test_re_split(self):
        for entry in RE_SPLIT_RESULTS:
            self.assertListEqual(re_split(entry[SEP], entry[STRING]), entry[RESULT])
