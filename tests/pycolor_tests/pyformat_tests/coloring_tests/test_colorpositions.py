import unittest

from src.pycolor.pycolor.pyformat.coloring import colorpositions

DATA = 'data'
COLOR_POS = 'color_pos'
RESULT = 'result'

class ColorPositionsTest(unittest.TestCase):
    def test_insert_color_data(self):
        entries = [
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

        for entry in entries:
            data = entry[DATA]
            colorpos = entry[COLOR_POS]
            with self.subTest(data=data, colorpos=colorpos):
                self.assertEqual(
                    entry[RESULT],
                    colorpositions.insert_color_data(data, colorpos)
                )

    def test_extract_color_data(self):
        entries = [
            {
                DATA: 'this is a test',
                RESULT: (
                    'this is a test',
                    {}
                )
            },
            {
                DATA: 'this \x1b[31mis\x1b[0m a \x1b[33;1mtest',
                RESULT: (
                    'this is a test',
                    {
                        5: '\x1b[31m',
                        7: '\x1b[0m',
                        10: '\x1b[33;1m'
                    }
                )
            },
            {
                DATA: 'this \x1b[31m\x1b[36mis\x1b[0m a \x1b[33;1mtest',
                RESULT: (
                    'this is a test',
                    {
                        5: '\x1b[31m\x1b[36m',
                        7: '\x1b[0m',
                        10: '\x1b[33;1m'
                    }
                )
            },
        ]

        for entry in entries:
            data = entry[DATA]
            with self.subTest(data=data):
                self.assertEqual(
                    entry[RESULT],
                    colorpositions.extract_color_data(data)
                )
