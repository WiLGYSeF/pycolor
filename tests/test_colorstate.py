import unittest

from src.pycolor import colorstate

STRING = 'string'
CODES = 'codes'
STATE = 'state'
STATE_PREV = 'state_prev'
RESULT = 'result'

class ColorStateTest(unittest.TestCase):
    def test_set_state_by_string(self):
        entries = [
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
                STRING: '\x1b[1;0m',
                RESULT: {}
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
            {
                STRING: '\x1b[1;38m',
                RESULT: {
                    colorstate.BOLD: True
                }
            },
            {
                STRING: '\x1b[1;38;5;256m',
                RESULT: {
                    colorstate.BOLD: True
                }
            },
            {
                STRING: '\x1b[8;38;2;256;170;0;1m',
                RESULT: {
                    colorstate.BOLD: True,
                    colorstate.CONCEAL: True,
                }
            },
            {
                STRING: '\x1b[31;38;5;130m',
                RESULT: {
                    colorstate.COLOR_FOREGROUND: '38;5;130',
                }
            },
            {
                STRING: '\x1b[38;5;130;31m',
                RESULT: {
                    colorstate.COLOR_FOREGROUND: '31',
                }
            },
        ]

        for entry in entries:
            string = entry[STRING]
            with self.subTest(string=string):
                state = colorstate.ColorState(string)

                expected_result = colorstate.DEFAULT_COLOR_STATE.copy()
                expected_result.update(entry[RESULT])
                self.assertDictEqual(expected_result, state.color_state)

    def test_set_state_by_codes(self):
        entries = [
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

        for entry in entries:
            codes = entry[CODES]
            with self.subTest(codes=codes):
                state = colorstate.ColorState(codes)

                expected_result = colorstate.DEFAULT_COLOR_STATE.copy()
                expected_result.update(entry[RESULT])
                self.assertDictEqual(expected_result, state.color_state)

    def test_get_string(self):
        entries = [
            {
                STATE: {},
                RESULT: ''
            },
            {
                STATE: {
                    colorstate.BOLD: True
                },
                RESULT: '\x1b[1m'
            },
            {
                STATE: {
                    colorstate.COLOR_FOREGROUND: '31',
                    colorstate.COLOR_BACKGROUND: '43',
                },
                RESULT: '\x1b[31;43m'
            },
            {
                STATE: {
                    colorstate.UNDERLINE: True,
                    colorstate.COLOR_FOREGROUND: '38;5;130',
                    colorstate.COLOR_BACKGROUND: '47',
                },
                RESULT: '\x1b[4;38;5;130;47m'
            },
            {
                STATE: {
                    colorstate.BLINK: False
                },
                STATE_PREV: {
                    colorstate.BLINK: True
                },
                RESULT: '\x1b[25m'
            },
            {
                STATE: {
                    colorstate.BLINK: False
                },
                STATE_PREV: {
                    colorstate.BLINK: False
                },
                RESULT: ''
            },
            {
                STATE: colorstate.ColorState('\x1b[2m'),
                RESULT: '\x1b[2m'
            },
            {
                STATE: [1, 25, 44],
                STATE_PREV: [3, 5, 34],
                RESULT: '\x1b[1;23;25;39;44m'
            }
        ]

        for entry in entries:
            e_state = entry[STATE]
            state_prev = entry.get(STATE_PREV)
            with self.subTest(state=e_state, state_prev=state_prev):
                state = colorstate.ColorState(e_state)
                if STATE_PREV in entry:
                    self.assertEqual(
                        entry[RESULT],
                        state.get_string(compare_state=colorstate.ColorState(state_prev))
                    )
                else:
                    self.assertEqual(entry[RESULT], str(state))
