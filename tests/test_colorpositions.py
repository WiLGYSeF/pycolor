import unittest

from src.pycolor import colorpositions


DATA = 'data'
COLOR_POS = 'color_pos'
RESULT = 'result'

INSERT_COLOR_DATA = [
    {
        DATA: 'this is a test',
        COLOR_POS: {},
        RESULT: 'this is a test'
    },
    {
        DATA: 'this is a test',
        COLOR_POS: {
            5: '\x1b[31m'
        },
        RESULT: 'this \x1b[31mis a test'
    },
    {
        DATA: 'this is a test',
        COLOR_POS: {
            5: '\x1b[31m',
            7: '\x1b[0m'
        },
        RESULT: 'this \x1b[31mis\x1b[0m a test'
    },
    {
        DATA: 'this is a test',
        COLOR_POS: {
            2: '\x1b[31m',
            5: '\x1b[32m',
            7: '\x1b[0m'
        },
        RESULT: 'th\x1b[31mis \x1b[32mis\x1b[0m a test'
    }
]


class ColorPositionsTest(unittest.TestCase):
    def test_insert_color_data(self):
        for entry in INSERT_COLOR_DATA:
            self.assertEqual(
                colorpositions.insert_color_data(entry[DATA], entry[COLOR_POS]),
                entry[RESULT]
            )
