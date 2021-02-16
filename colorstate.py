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

    COLOR_FOREGROUND: '39',
    COLOR_BACKGROUND: '49'
}


class ColorState:
    def __init__(self):
        self.color_state = {}
        self.reset()

    def reset(self):
        self.color_state = DEFAULT_COLOR_STATE.copy()

    def set_state_by_string(self, string):
        codelist = []
        for match in re.finditer(r'\x1b\[([0-9;]+)m', string):
            codes = list(map(
                lambda x: int(x),
                filter(
                    lambda x: len(x) != 0,
                    match[1].split(';')
                )
            ))

            codelist.extend(self.set_special_color_states(codes))

        self.set_state_by_codes(codelist)

    def set_special_color_states(self, codes):
        newcodes = []

        i = 0
        while i < len(codes):
            code = codes[i]
            if code not in (38, 48):
                newcodes.append(code)
                i += 1
                continue

            if i + 1 == len(codes):
                break

            color = None
            if codes[i + 1] == 5:
                if i + 2 < len(codes):
                    if codes[i + 2] < 256:
                        color = '%d;5;%d' % (code, codes[i + 2])
                    i += 2
                else:
                    i = len(codes)
            elif codes[i + 1] == 2:
                if i + 4 < len(codes):
                    if codes[i + 2] < 256 and codes[i + 3] < 256 and codes[i + 4] < 256:
                        color = '%d;2;%d;%d;%d' % (
                            code,
                            codes[i + 2],
                            codes[i + 3],
                            codes[i + 4]
                        )
                    i += 4
                else:
                    i = len(codes)

            if color is not None:
                if code == 38:
                    self.color_state[COLOR_FOREGROUND] = color
                    newcodes = list(filter(
                        lambda x: not (x >= 30 and x <= 39),
                        newcodes
                    ))
                elif code == 48:
                    self.color_state[COLOR_BACKGROUND] = color
                    newcodes = list(filter(
                        lambda x: not (x >= 40 and x <= 49),
                        newcodes
                    ))
            i += 1

        return newcodes

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
            if code == 0:
                self.reset()
            elif code in style_code_enable:
                self.color_state[style_code_enable[code]] = True
            elif code in style_code_disable:
                self.color_state[style_code_disable[code]] = False
            elif (code >= 30 and code <= 39) or (code >= 90 and code <= 97):
                self.color_state[COLOR_FOREGROUND] = str(code)
            elif (code >= 40 and code <= 49) or (code >= 100 and code <= 107):
                self.color_state[COLOR_BACKGROUND] = str(code)
