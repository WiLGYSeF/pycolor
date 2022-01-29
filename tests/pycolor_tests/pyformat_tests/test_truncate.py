import unittest

from src.pycolor.pycolor import pyformat

STRING = 'string'
RESULT = 'result'

class TruncateTest(unittest.TestCase):
    def test_truncate_left(self):
        entries = [
            {
                STRING: '%(trunc:100,left,...)this is a test%(end)',
                RESULT: 'this is a test'
            },
            {
                STRING: '%(trunc:8,left,...)this is a test%(end)',
                RESULT: '... test'
            },
            {
                STRING: '%(trunc:8,left,...,no)this is a test%(end)',
                RESULT: '...s a test'
            },
            {
                STRING: '%(trunc:-8,left,...,no)this is a test%(end)',
                RESULT: 'this is a test'
            },
            {
                STRING: '%(trunc:8,zzz,...,no)this is a test%(end)',
                RESULT: '...s a test'
            },
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                self.assertEqual(entry[RESULT], pyformat.fmt_str(string))

    def test_truncate_middle(self):
        entries = [
            {
                STRING: '%(trunc:100,middle,...)this is a test%(end)',
                RESULT: 'this is a test'
            },
            {
                STRING: '%(trunc:8,middle,...)this is a test%(end)',
                RESULT: 'th...est'
            },
            {
                STRING: '%(trunc:8,middle,\x1b[1;32m...\x1b[0m,no)this is a test%(end)',
                RESULT: 'this\x1b[1;32m...\x1b[0mtest'
            },
            {
                STRING: '%(trunc:13,middle,...,no)this is an uneven test%(end)',
                RESULT: 'this i...en test'
            },
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                self.assertEqual(entry[RESULT], pyformat.fmt_str(string))

    def test_truncate_right(self):
        entries = [
            {
                STRING: '%(trunc:100,right,...)this is a test%(end)',
                RESULT: 'this is a test'
            },
            {
                STRING: '%(trunc:8,right,...)this is a test%(end)',
                RESULT: 'this ...'
            },
            {
                STRING: '%(trunc:8,right,...,no)this is a test%(end)',
                RESULT: 'this is ...'
            },
            {
                STRING: '%(trunc:8,right)this is a test%(end)',
                RESULT: 'this is '
            }
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                self.assertEqual(entry[RESULT], pyformat.fmt_str(string))
