import typing

ColorPositions = typing.Dict[int, str]

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
