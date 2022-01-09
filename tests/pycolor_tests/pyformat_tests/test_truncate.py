import unittest

from src.pycolor.pycolor import pyformat

STRING = 'string'
RESULT = 'result'

class TruncateTest(unittest.TestCase):
    def test_truncate_start(self):
        entries = [
            {
                STRING: '%T(this is a test;...;start,8)',
                RESULT: '... test'
            },
            {
                STRING: '%T(this is a test;...;start-add,8)',
                RESULT: '...s a test'
            },
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                self.assertEqual(entry[RESULT], pyformat.fmt_str(string))

    def test_truncate_mid(self):
        entries = [
            {
                STRING: '%T(this is a test;...;mid,8)',
                RESULT: 'th...est'
            },
            {
                STRING: '%T(this is a test;\x1b[2\\;33m...\x1b[0m;mid-add,8)',
                RESULT: 'this\x1b[2;33m...\x1b[0mtest'
            },
            {
                STRING: '%T(this is an uneven test;...;mid-add,13)',
                RESULT: 'this i...en test'
            },
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                self.assertEqual(entry[RESULT], pyformat.fmt_str(string))

    def test_truncate_end(self):
        entries = [
            {
                STRING: '%T(this is a test;...;end,100)',
                RESULT: 'this is a test'
            },
            {
                STRING: '%T(this is a test;...;end,8)',
                RESULT: 'this ...'
            },
            {
                STRING: '%T(this is a test;...;end-add,8)',
                RESULT: 'this is ...'
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
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                self.assertEqual(entry[RESULT], pyformat.fmt_str(string))

    def test_truncate_fail(self):
        entries = [
            {
                STRING: '%T(this is a test;...;invalid,8)',
                RESULT: ValueError()
            },
            {
                STRING: '%T(this is a test;...;end-add,-8)',
                RESULT: ValueError()
            },
            {
                STRING: '%T(this is a test;...;-8)',
                RESULT: ValueError()
            },
            {
                STRING: '%T(this is a test;...;end)',
                RESULT: ValueError()
            },
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                with self.assertRaises(type(entry[RESULT])):
                    pyformat.fmt_str(string)
