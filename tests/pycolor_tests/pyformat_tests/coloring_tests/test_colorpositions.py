import unittest

from src.pycolor.pycolor.pyformat.coloring import colorpositions

DATA = 'data'
COLOR_POS = 'color_pos'
OFFSET = 'offset'
REPLACE_RANGES = 'replace_ranges'
RESULT = 'result'

class ColorPositionsTest(unittest.TestCase):
    def test_update_color_positions(self):
        entries = [
            {
                COLOR_POS: {
                    5: '\x1b[31m',
                    8: '\x1b[0m'
                },
                DATA: {
                    6: '\x1b[32m',
                    8: '\x1b[1;5m'
                },
                RESULT: {
                    5: '\x1b[31m',
                    6: '\x1b[32m',
                    8: '\x1b[0m\x1b[1;5m'
                }
            }
        ]

        for entry in entries:
            colorpos = entry[COLOR_POS]
            data = entry[DATA]
            with self.subTest(colorpos=colorpos, data=data):
                colorpositions.update_color_positions(colorpos, data)
                self.assertDictEqual(entry[RESULT], colorpos)

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

    def test_update_color_positions_replace_ranges(self):
        add_tests = [
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    12: '\x1b[1;35m',
                },
                REPLACE_RANGES: [
                    (
                        (5, 7),
                        (5, 10)
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    11: '\x1b[32m',
                    15: '\x1b[1;35m',
                }
            },
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    12: '\x1b[1;35m',
                },
                REPLACE_RANGES: [
                    (
                        (5, 9),
                        (5, 14)
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    17: '\x1b[1;35m',
                }
            },
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    12: '\x1b[1;35m',
                },
                REPLACE_RANGES: [
                    (
                        (4, 6),
                        (4, 8)
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    10: '\x1b[32m',
                    14: '\x1b[1;35m',
                }
            },
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    12: '\x1b[1;35m',
                },
                REPLACE_RANGES: [
                    (
                        (6, 8),
                        (6, 10)
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    14: '\x1b[1;35m',
                }
            },
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    14: '\x1b[1;35m',
                    19: '\x1b[31m',
                },
                REPLACE_RANGES: [
                    (
                        (5, 9),
                        (5, 14)
                    ),
                    (
                        (12, 15),
                        (17, 20)
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    24: '\x1b[31m'
                }
            },
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    14: '\x1b[1;35m',
                    19: '\x1b[31m',
                },
                REPLACE_RANGES: [
                    (
                        (5, 7),
                        (5, 9)
                    ),
                    (
                        (7, 15),
                        (9, 22)
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    26: '\x1b[31m'
                }
            },
        ]

        remove_tests = [
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    12: '\x1b[1;35m',
                    13: '\x1b[0m',
                    18: '\x1b[1m',
                },
                REPLACE_RANGES: [
                    (
                        (6, 10),
                        (6, 7)
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    9: '\x1b[1;35m',
                    10: '\x1b[0m',
                    15: '\x1b[1m',
                }
            },
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    12: '\x1b[1;35m',
                },
                REPLACE_RANGES: [
                    (
                        (4, 6),
                        (4, 4)
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    6: '\x1b[32m',
                    10: '\x1b[1;35m',
                }
            },
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    12: '\x1b[1;35m',
                },
                REPLACE_RANGES: [
                    (
                        (6, 8),
                        (6, 7)
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    11: '\x1b[1;35m',
                }
            },
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    12: '\x1b[1;35m',
                    13: '\x1b[0m',
                    18: '\x1b[1m',
                },
                REPLACE_RANGES: [
                    (
                        (6, 10),
                        (6, 7)
                    ),
                    (
                        (11, 13),
                        (8, 8),
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    13: '\x1b[1m',
                }
            },
            {
                COLOR_POS: {
                    4: '\x1b[31m',
                    8: '\x1b[32m',
                    14: '\x1b[1;35m',
                    19: '\x1b[31m',
                },
                REPLACE_RANGES: [
                    (
                        (5, 7),
                        (5, 9)
                    ),
                    (
                        (7, 15),
                        (9, 15)
                    )
                ],
                RESULT: {
                    4: '\x1b[31m',
                    19: '\x1b[31m'
                }
            },
        ]

        entries = [*add_tests, *remove_tests]

        for entry in entries:
            colorpos = entry[COLOR_POS]
            replace_ranges = entry[REPLACE_RANGES]
            with self.subTest(colorpos=colorpos, replace_ranges=replace_ranges):
                self.assertDictEqual(
                    entry[RESULT],
                    colorpositions.update_color_positions_replace_ranges(
                        colorpos,
                        replace_ranges
                    )
                )

    def test_offset_color_positions(self):
        entries = [
            {
                COLOR_POS: {
                    5: '\x1b[31m',
                    8: '\x1b[0m'
                },
                OFFSET: 6,
                RESULT: {
                    11: '\x1b[31m',
                    14: '\x1b[0m'
                }
            }
        ]

        for entry in entries:
            colorpos = entry[COLOR_POS]
            offset = entry[OFFSET]
            with self.subTest(colorpos=colorpos, offset=offset):
                self.assertDictEqual(
                    entry[RESULT],
                    colorpositions.offset_color_positions(colorpos, offset)
                )
