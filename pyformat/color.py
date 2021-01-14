import re


def get_color(colorstr):
    val = ';'.join(filter(
        lambda x: x is not None,
        [ _colorval(clr) for clr in colorstr.split(';') ]
    ))
    if len(val) == 0:
        return None

    return '\x1b[%sm' % val

def _colorval(color):
    colors = {
        'reset': 0,
        'normal': 0,
        'bold': 1,
        'bright': 1,
        'dim': 2,
        'italic': 3,
        'underline': 4,
        'underlined': 4,
        'blink': 5,
        'invert': 7,
        'reverse': 7,
        'hidden': 8,
        'conceal': 8,
        'strikethrough': 9,
        'crossed': 9,
        'crossedout': 9,

        'res': 0,
        'nor': 0,
        'bol': 1,
        'bri': 1,
        'dim': 2,
        'ita': 3,
        'und': 4,
        'bli': 5,
        'inv': 7,
        'rev': 7,
        'hid': 8,
        'con': 8,
        'str': 9,
        'cro': 9,

        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'gray': 37,
        'grey': 37,
        'lightgray': 37,
        'lightgrey': 37,
        'default': 39,

        'k': 30, #black
        'r': 31, #red
        'g': 32, #green
        'y': 33, #yellow
        'b': 34, #blue
        'm': 35, #magenta
        'c': 36, #cyan
        'e': 37, #grey

        'overline': 53,
        'overlined': 53,

        'ove': 53,

        'darkgray': 90,
        'darkgrey': 90,
        'lightred': 91,
        'lightgreen': 92,
        'lightyellow': 93,
        'lightblue': 94,
        'lightmagenta': 95,
        'lightcyan': 96,
        'white': 97,

        'de': 90,
        'lk': 90,
        'lr': 91,
        'lg': 92,
        'ly': 93,
        'lb': 94,
        'lm': 95,
        'lc': 96,
        'w': 97,
    }

    if len(color) == 0:
        return None

    toggle = False
    if color[0] == '^':
        color = color[1:]
        toggle = True

    try:
        return '%d;5;%d' % (
            48 if toggle else 38,
            int(color)
        )
    except ValueError:
        pass

    try:
        red, green, blue = hex_to_rgb(color)
        return '%d;2;%d;%d;%d' % (
            48 if toggle else 38,
            red,
            green,
            blue
        )
    except ValueError:
        pass

    if color.lower() not in colors:
        return None

    val = colors[color.lower()]
    if toggle:
        if val >= 30 and val <= 39 or val >= 90 and val <= 97:
            val += 10
        elif val >= 1 and val <= 8:
            val += 20
        elif val == 53:
            val = 55

    return str(val)

def hex_to_rgb(string):
    match = re.fullmatch(
        r'(?:0x)?(?:(?P<six>[0-9a-f]{6})|(?P<three>[0-9a-f]{3}))',
        string
    )
    if match is None:
        raise ValueError()

    groups = match.groupdict()
    if groups['three'] is not None:
        three = groups['three']
        return int(three[0] * 2, 16), int(three[1] * 2, 16), int(three[2] * 2, 16)

    six = groups['six']
    return int(six[0:2], 16), int(six[2:4], 16), int(six[4:6], 16)
