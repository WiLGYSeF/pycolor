import re
import unittest

from src.pycolor.strman.split import re_split

SEP = 'sep'
STRING = 'string'
RESULT = 'result'

class SplitTest(unittest.TestCase):
    def test_re_split(self):
        entries = [
            {
                SEP: None,
                STRING: 'this is a test',
                RESULT: ['this is a test']
            },
            {
                SEP: re.compile(' '),
                STRING: 'this is a test',
                RESULT: [
                    'this', ' ', 'is', ' ', 'a', ' ', 'test'
                ]
            },
            {
                SEP: re.compile(' +'),
                STRING: 'this   is    a test',
                RESULT: [
                    'this', '   ', 'is', '    ', 'a', ' ', 'test'
                ]
            },
            {
                SEP: re.compile(' '),
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

        for entry in entries:
            sep = entry[SEP]
            string = entry[STRING]
            with self.subTest(regex=sep, string=string):
                self.assertListEqual(
                    entry[RESULT],
                    list(re_split(sep, string))
                )
