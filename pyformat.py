FORMAT_CHAR_VALID = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'


def format_string(string, context=None):
    if context is None:
        context = {}

    newstring = ''
    idx = 0

    while idx < len(string):
        char = string[idx]
        if char == '\\':
            newstring += '\\'
            if idx < len(string) - 1:
                newstring += string[idx + 1]

            idx += 2
            continue

        if char == '%':
            formatter, newidx = get_formatter(string, idx)
            if formatter is not None:
                newstring += do_format(string, formatter, idx, newidx, context)
                idx = newidx
                continue

        newstring += char
        idx += 1

    return newstring

def do_format(string, formatter, idx, newidx, context):
    if formatter[0] == 'C':
        color = get_color(formatter[1:])
        return color if color is not None else ''

    if 'match' in context:
        if formatter[0] == 'G':
            try:
                group = int(formatter[1:])
            except ValueError:
                group = formatter[1:]

            try:
                # FIXME: should not decode here
                return context['match'][group].decode('utf-8')
            except IndexError:
                return ''

    return string[idx:newidx]

def get_formatter(string, idx):
    if idx >= len(string) or string[idx] != '%':
        return None, idx

    paren = False
    had_paren = False
    idx += 1

    if idx >= len(string):
        return None, idx

    if string[idx] == '(':
        paren = True
        had_paren = True
        idx += 1

    startidx = idx

    while idx < len(string):
        char = string[idx]
        if not paren and char not in FORMAT_CHAR_VALID:
            break

        if char == ')':
            paren = False
            idx += 1
            break

        idx += 1

    if had_paren:
        formatter = string[startidx:idx - 1]
    else:
        formatter = string[startidx:idx]

    return formatter, idx

def get_color(colorstr):
    def _colorval(color):
        colors = {
            'reset': 0,
            'bold': 1,
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

        return val

    val = ';'.join(filter(
        lambda x: x != 'None',
        [ str(_colorval(clr)) for clr in colorstr.split(';') ]
    ))

    if len(val) == 0:
        return None

    return '\x1b[%sm' % val
