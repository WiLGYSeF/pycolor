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

ANSI_REGEX = re.compile(r'\x1b\[([0-9;]+)m')


class ColorState:
    def __init__(self, state=None):
        self.color_state = {}
        self.state_changed = set()
        self.reset()

        if state is not None:
            self.set(state)

    def reset(self):
        self.color_state = DEFAULT_COLOR_STATE.copy()
        self.state_changed = set()

    def copy(self):
        return ColorState(self.color_state)

    def set(self, value):
        if isinstance(value, ColorState):
            self.set_state_by_state(value)
        elif isinstance(value, dict):
            self.set_state_by_dict(value)
        elif isinstance(value, str):
            self.set_state_by_string(value)
        elif isinstance(value, (list, tuple)):
            self.set_state_by_codes(value)
        else:
            raise ValueError()

    def set_state_by_state(self, state):
        for key, val in state.color_state.items():
            self.color_state[key] = val
        for val in state.state_changed:
            self.state_changed.add(val)

    def set_state_by_dict(self, dct):
        for key, val in dct.items():
            self.color_state[key] = val
            self.state_changed.add(key)

    def set_state_by_string(self, string):
        codelist = []
        for match in ANSI_REGEX.finditer(string):
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
                    self.state_changed.add(COLOR_FOREGROUND)

                    newcodes = list(filter(
                        lambda x: not (x >= 30 and x <= 39),
                        newcodes
                    ))
                elif code == 48:
                    self.color_state[COLOR_BACKGROUND] = color
                    self.state_changed.add(COLOR_BACKGROUND)

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
                code = style_code_enable[code]
                self.color_state[code] = True
                self.state_changed.add(code)
            elif code in style_code_disable:
                code = style_code_disable[code]
                self.color_state[code] = False
                self.state_changed.add(code)
            elif (code >= 30 and code <= 39) or (code >= 90 and code <= 97):
                self.color_state[COLOR_FOREGROUND] = str(code)
                self.state_changed.add(COLOR_FOREGROUND)
            elif (code >= 40 and code <= 49) or (code >= 100 and code <= 107):
                self.color_state[COLOR_BACKGROUND] = str(code)
                self.state_changed.add(COLOR_BACKGROUND)

    def diff_keys(self, state):
        diff_keys = []

        for key, val in self.color_state.items():
            if val != state.color_state[key]:
                diff_keys.append(key)

        return diff_keys

    def get_state_by_keys(self, keys):
        state = {}
        for k in keys:
            state[k] = self.color_state[k]
        return state

    def get_changed_state(self, compare_state=None):
        if compare_state is None:
            compare_state = ColorState()
        return self.get_state_by_keys(self.diff_keys(compare_state))

    def get_string(self, compare_state=None):
        styles = {
            BOLD: 1,
            DIM: 2,
            ITALIC: 3,
            UNDERLINE: 4,
            BLINK: 5,
            INVERT: 7,
            CONCEAL: 8,
            STRIKETHROUGH: 9,

            OVERLINE: 53
        }

        state = self.get_changed_state(compare_state)
        codes = []

        for key, val in styles.items():
            if key in state:
                if state[key]:
                    codes.append(str(val))
                else:
                    codes.append(str(val + 20))

        if COLOR_FOREGROUND in state:
            codes.append(state[COLOR_FOREGROUND])
        if COLOR_BACKGROUND in state:
            codes.append(state[COLOR_BACKGROUND])

        if len(codes) == 0:
            return ''
        return '\x1b[%sm' % ';'.join(codes)

    @staticmethod
    def from_str(string):
        state = ColorState()
        state.set_state_by_string(string)
        return state

    def __str__(self):
        return self.get_string()