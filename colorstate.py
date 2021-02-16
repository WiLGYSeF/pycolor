import re


BOLD = 'bold'
DIM = 'dim'
ITALIC = 'italic'
UNDERLINE = 'underline'
BLINK = 'blink'
INVERT = 'invert'
CONCEAL = 'conceal'
STRIKETHROUGH = 'strike'

OVERLINE = 'overline'

COLOR_FOREGROUND = 'color_foreground'
COLOR_BACKGROUND = 'color_background'

DEFAULT_COLOR_STATE = {
    BOLD: False,
    DIM: False,
    ITALIC: False,
    UNDERLINE: False,
    BLINK: False,
    INVERT: False,
    CONCEAL: False,
    STRIKETHROUGH: False,

    OVERLINE: False,

    COLOR_FOREGROUND: 39,
    COLOR_BACKGROUND: 49
}


class ColorState:
    def __init__(self):
        self.color_state = DEFAULT_COLOR_STATE.copy()

    def set_state_by_string(self, string):
        codes = []
        for match in re.finditer(r'\x1b\[([0-9;]+)m', string):
            matched_codes = map(
                lambda x: int(x),
                filter(
                    lambda x: len(x) != 0,
                    match[1].split(';')
                )
            )
            codes.extend(matched_codes)

        self.set_state_by_codes(codes)

    def set_state_by_codes(self, codes):
        style_code_enable = {
            1: BOLD,
            2: DIM,
            3: ITALIC,
            4: UNDERLINE,
            5: BLINK,
            7: INVERT,
            8: CONCEAL,
            9: STRIKETHROUGH,

            53: OVERLINE
        }

        style_code_disable = {
            21: BOLD,
            22: DIM,
            23: ITALIC,
            24: UNDERLINE,
            25: BLINK,
            27: INVERT,
            28: CONCEAL,
            29: STRIKETHROUGH,

            55: OVERLINE
        }

        for code in codes:
            if code in style_code_enable:
                self.color_state[style_code_enable[code]] = True
            elif code in style_code_disable:
                self.color_state[style_code_disable[code]] = False
