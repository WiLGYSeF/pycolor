import unittest

from pycolor_class import Pycolor


COLOR_POSITION = 'color_position'
POS = 'pos'
RESULT = 'result'

UPDATE_COLOR_POSITIONS = [
    {
        COLOR_POSITION: {},
        POS: {},
        RESULT: {}
    },
    {
        COLOR_POSITION: {
            5: '\x1b[31m',
            9: '\x1b[0m'
        },
        POS: {},
        RESULT: {
            5: '\x1b[31m',
            9: '\x1b[0m'
        }
    },
    {
        COLOR_POSITION: {
            5: '\x1b[31m',
            9: '\x1b[0m'
        },
        POS: {
            1: '\x1b[34m'
        },
        RESULT: {
            1: '\x1b[34m'
        }
    },
    {
        COLOR_POSITION: {
            5: '\x1b[31m',
            9: '\x1b[0m'
        },
        POS: {
            7: '\x1b[34m'
        },
        RESULT: {
            5: '\x1b[31m',
            7: '\x1b[34m'
        }
    },
    {
        COLOR_POSITION: {
            5: '\x1b[31m',
            9: '\x1b[0m'
        },
        POS: {
            12: '\x1b[34m'
        },
        RESULT: {
            5: '\x1b[31m',
            9: '\x1b[0m',
            12: '\x1b[34m'
        }
    },
    {
        COLOR_POSITION: {
            5: '\x1b[31m',
            9: '\x1b[0m'
        },
        POS: {
            6: '\x1b[34m',
            7: '\x1b[0m'
        },
        RESULT: {
            5: '\x1b[31m',
            6: '\x1b[34m',
            7: '\x1b[0m\x1b[31m',
            9: '\x1b[0m'
        }
    },
    {
        COLOR_POSITION: {
            5: '\x1b[31m',
            9: '\x1b[0m'
        },
        POS: {
            6: '\x1b[34m',
            11: '\x1b[0m'
        },
        RESULT: {
            5: '\x1b[31m',
            6: '\x1b[34m',
            11: '\x1b[0m\x1b[31m'
        }
    },
    {
        COLOR_POSITION: {
            5: '\x1b[31m',
            9: '\x1b[0m'
        },
        POS: {
            6: '\x1b[34m',
            8: '\x1b[0m',
            11: '\x1b[36m'
        },
        RESULT: {
            5: '\x1b[31m',
            6: '\x1b[34m',
            8: '\x1b[0m\x1b[31m',
            9: '\x1b[0m',
            11: '\x1b[36m'
        }
    },
]


class UpdateColorPositionsTest(unittest.TestCase):
    def test_update_color_positions(self):
        for entry in UPDATE_COLOR_POSITIONS:
            Pycolor.update_color_positions(entry[COLOR_POSITION], entry[POS])
            self.assertDictEqual(entry[COLOR_POSITION], entry[RESULT])
