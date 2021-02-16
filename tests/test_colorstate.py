import unittest

import colorstate


CODES = 'codes'
RESULT = 'result'

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
]


class ColorState(unittest.TestCase):
    def test_set_state_by_codes(self):
        for entry in SET_STATE_BY_CODES:
            state = colorstate.ColorState()
            state.set_state_by_codes(entry[CODES])

            expected_result = colorstate.DEFAULT_COLOR_STATE.copy()
            expected_result.update(entry[RESULT])

            self.assertDictEqual(state.color_state, expected_result)
