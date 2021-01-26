import unittest

from pycolor_class import Pycolor


DATA = 'data'
COLOR_POS = 'color_pos'
RESULT = 'result'

INSERT_COLOR_DATA = [
    {
        DATA: b'this is a test',
        COLOR_POS: {},
        RESULT: b'this is a test'
    },
    {
        DATA: b'this is a test',
        COLOR_POS: {
            5: '\x1b[31m'
        },
        RESULT: b'this \x1b[31mis a test'
    },
    {
        DATA: b'this is a test',
        COLOR_POS: {
            5: '\x1b[31m',
            7: '\x1b[0m'
        },
        RESULT: b'this \x1b[31mis\x1b[0m a test'
    },
]


class InsertColorDataTest(unittest.TestCase):
    def test_insert_color_data(self):
        for entry in INSERT_COLOR_DATA:
            self.assertEqual(
                Pycolor.insert_color_data(entry[DATA], entry[COLOR_POS]),
                entry[RESULT]
            )
