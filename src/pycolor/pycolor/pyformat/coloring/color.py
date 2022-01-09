import re
import typing

from . import COLORS

RAW_REGEX = re.compile(r'r(?:aw)?([0-9;]+)')
ANSI_REGEX = re.compile(r'\x1b\[([0-9;]+)m')
HEX_REGEX = re.compile(r'(?:0x)?(?:(?P<six>[0-9a-f]{6})|(?P<three>[0-9a-f]{3}))')

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
