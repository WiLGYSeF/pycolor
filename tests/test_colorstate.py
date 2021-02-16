import unittest

import colorstate


STRING = 'string'
CODES = 'codes'
RESULT = 'result'

SET_STATE_BY_STRING = [
    {
        STRING: '',
        RESULT: {}
    },
    {
        STRING: '\x1b[1m',
        RESULT: {
            colorstate.BOLD: True
        }
    },
    {
        STRING: '\x1b[3mtesting\x1b[9m',
        RESULT: {
            colorstate.ITALIC: True,
            colorstate.STRIKETHROUGH: True
        }
    },
    {
        STRING: '\x1b[3;9m',
        RESULT: {
            colorstate.ITALIC: True,
            colorstate.STRIKETHROUGH: True
        }
    },
    {
        STRING: '\x1b[3;;9m',
        RESULT: {
            colorstate.ITALIC: True,
            colorstate.STRIKETHROUGH: True
        }
    },
    {
        STRING: '\x1b[;m',
        RESULT: {}
    },
    {
        STRING: '\x1b[31m',
        RESULT: {
            colorstate.COLOR_FOREGROUND: '31'
        }
    },
    {
        STRING: '\x1b[1;38;5;130;5m',
        RESULT: {
            colorstate.BOLD: True,
            colorstate.BLINK: True,
            colorstate.COLOR_FOREGROUND: '38;5;130',
        }
    },
    {
        STRING: '\x1b[5;48;2;255;170;0;1m',
        RESULT: {
            colorstate.BOLD: True,
            colorstate.BLINK: True,
            colorstate.COLOR_BACKGROUND: '48;2;255;170;0',
        }
    },
    {
        STRING: '\x1b[1;38;5m',
        RESULT: {
            colorstate.BOLD: True
        }
    },
    {
        STRING: '\x1b[5;48;2;255;170;m',
        RESULT: {
            colorstate.BLINK: True
        }
    },
]

SET_STATE_BY_CODES = [
    {
        CODES: [-4],
        RESULT: {}
    },
    {
        CODES: [1],
        RESULT: {
            colorstate.BOLD: True
        }
    },
    {
        CODES: [3, 9],
        RESULT: {
            colorstate.ITALIC: True,
            colorstate.STRIKETHROUGH: True,
        }
    },
    {
        CODES: [3, 9, 23, 27],
        RESULT: {
            colorstate.STRIKETHROUGH: True,
        }
    },
    {
        CODES: [31],
        RESULT: {
            colorstate.COLOR_FOREGROUND: '31',
        }
    },
    {
        CODES: [31, 43],
        RESULT: {
            colorstate.COLOR_FOREGROUND: '31',
            colorstate.COLOR_BACKGROUND: '43',
        }
    },
]


class ColorState(unittest.TestCase):
    def test_set_state_by_string(self):
        for entry in SET_STATE_BY_STRING:
            state = colorstate.ColorState()
            state.set_state_by_string(entry[STRING])

            expected_result = colorstate.DEFAULT_COLOR_STATE.copy()
            expected_result.update(entry[RESULT])

            self.assertDictEqual(state.color_state, expected_result)


    def test_set_state_by_codes(self):
        for entry in SET_STATE_BY_CODES:
            state = colorstate.ColorState()
            state.set_state_by_codes(entry[CODES])

            expected_result = colorstate.DEFAULT_COLOR_STATE.copy()
            expected_result.update(entry[RESULT])

            self.assertDictEqual(state.color_state, expected_result)
