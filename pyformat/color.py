def get_color(colorstr):
    def _colorval(color):
        colors = {
            'reset': 0,
            'bold': 1,
            'bright': 1,
            'dim': 2,
            'underline': 4,
            'underlined': 4,
            'blink': 5,
            'invert': 7,
            'reverse': 7,
            'hidden': 8,
            'black': 30,
            'red': 31,
            'green': 32,
            'yellow': 33,
            'blue': 34,
            'magenta': 35,
            'cyan': 36,
            'lightgray': 37,
            'lightgrey': 37,
            'default': 39,
            'darkgray': 90,
            'darkgrey': 90,
            'lightred': 91,
            'lightgreen': 92,
            'lightyellow': 93,
            'lightblue': 94,
            'lightmagenta': 95,
            'lightcyan': 96,
            'white': 97
        }

        if len(color) == 0:
            return None

        background = False
        if color[0] == '^':
            color = color[1:]
            background = True

        try:
            return '%d;5;%d' % (
                48 if background else 38,
                int(color)
            )
        except ValueError:
            pass

        if color.lower() not in colors:
            return None

        val = colors[color.lower()]
        if background:
            if val >= 30:
                val += 10
            elif val >= 1 and val <= 8:
                val += 20

        return str(val)

    val = ';'.join(filter(
        lambda x: x is not None,
        [ _colorval(clr) for clr in colorstr.split(';') ]
    ))

    if len(val) == 0:
        return None

    return '\x1b[%sm' % val