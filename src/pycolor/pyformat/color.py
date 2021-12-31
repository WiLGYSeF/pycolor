import re
import typing

RAW_REGEX = re.compile(r'r(?:aw)?([0-9;]+)')
ANSI_REGEX = re.compile(r'\x1b\[([0-9;]+)m')
HEX_REGEX = re.compile(r'(?:0x)?(?:(?P<six>[0-9a-f]{6})|(?P<three>[0-9a-f]{3}))')

COLORS = {
    'black': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'gray': 37,
    'grey': 37,
    'default': 39,

    'k': 30, #black
    'r': 31, #red
    'g': 32, #green
    'y': 33, #yellow
    'b': 34, #blue
    'm': 35, #magenta
    'c': 36, #cyan
    'e': 37, #grey

    'darkgray': 90,
    'darkgrey': 90,
    'lightblack': 90,
    'lightred': 91,
    'lightgreen': 92,
    'lightyellow': 93,
    'lightblue': 94,
    'lightmagenta': 95,
    'lightcyan': 96,
    'lightgray': 97,
    'lightgrey': 97,
    'white': 97,

    'de': 90, #darkgrey
    'lk': 90, #darkgrey
    'lr': 91, #lightred
    'lg': 92, #lightgreen
    'ly': 93, #lightyellow
    'lb': 94, #lightblue
    'lm': 95, #lightmagenta
    'lc': 96, #lightcyan
    'le': 97, #lightgrey (white)
    'w': 97,  #white
}

STYLES = {
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
    'strike': 9,
    'strikethrough': 9,
    'crossed': 9,
    'crossedout': 9,

    'z': 0,
    'res': 0,
    'nor': 0,
    'bol': 1,
    'bri': 1,
    'ita': 3,
    'ul': 4,
    'und': 4,
    'bli': 5,
    'inv': 7,
    'rev': 7,
    'hid': 8,
    'con': 8,
    'str': 9,
    'cro': 9,

    'overline': 53,
    'overlined': 53,

    'ol': 53,
    'ove': 53,
}

# STYLES are considered colors
COLORS.update(STYLES)

def get_color(colorstr: str, aliases: typing.Dict[str, str] = None) -> typing.Optional[str]:
    """Converts color string to ANSI color string

    Args:
        colorstr (str): Color string
        aliases (dict): Optional color alias map

    Returns:
        str: ANSI color string
    """
    match = RAW_REGEX.fullmatch(colorstr)
    if match:
        return '\x1b[%sm' % match[1]

    colors: typing.List[str] = list(filter(
        lambda x: x is not None,
        ( _colorval(clr, aliases) for clr in colorstr.split(';') ) # type: ignore
    ))

    return '\x1b[%sm' % ';'.join(colors) if len(colors) != 0 else None

def _colorval(color: str, aliases: typing.Dict[str, str] = None) -> typing.Optional[str]:
    if aliases is not None and color in aliases:
        color = aliases[color]

    if len(color) == 0:
        return None

    toggle = False
    if color[0] == '^':
        color = color[1:]
        toggle = True

    val = COLORS.get(color.lower())
    if val is not None:
        if toggle:
            if val >= 30 and val <= 39 or val >= 90 and val <= 97:
                val += 10
            elif val >= 1 and val <= 8:
                val += 20
            elif val == 53:
                val = 55

        return str(val)

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

    return None

def remove_ansi_color(string: str) -> str:
    """Removes ANSI colors from string

    Args:
        string (str): String

    Returns:
        str: String without ANSI colors
    """
    return ANSI_REGEX.sub('', string)

def is_ansi_reset(string: str) -> bool:
    """Checks if the color string ends with a reset

    Args:
        string (str): ANSI color string

    Returns:
        bool: Returnss true if the color string ends with reset
    """
    match = ANSI_REGEX.fullmatch(string)
    if match is None:
        return False
    return not any((char not in '0;' for char in match[1].split(';')[-1]))

def hex_to_rgb(string: str) -> typing.Tuple[int, int, int]:
    """Converts color string to rgb

    Args:
        string (str): Hex color string

    Returns:
        tuple: RGB colors
    """
    match = HEX_REGEX.fullmatch(string)
    if match is None:
        raise ValueError()

    groups = match.groupdict()
    if groups['three'] is not None:
        three = groups['three']
        return int(three[0] * 2, 16), int(three[1] * 2, 16), int(three[2] * 2, 16)

    six = groups['six']
    return int(six[0:2], 16), int(six[2:4], 16), int(six[4:6], 16)
