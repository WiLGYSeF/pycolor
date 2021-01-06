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
                if formatter[0] == 'C':
                    color = get_color(formatter[1:])
                    if color is not None:
                        newstring += color
                elif len(context) != 0:
                    if 'match' in context:
                        if formatter[0] == 'G':
                            try:
                                group = int(formatter[1:])
                            except ValueError:
                                group = formatter[1:]

                            try:
                                # FIXME: should not decode here
                                newstring += context['match'][group].decode('utf-8')
                            except IndexError:
                                pass
                else:
                    newstring += string[idx:newidx]

                idx = newidx
                continue

        newstring += char

        idx += 1

    return newstring

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

def get_color(color):
    colors = {
        'reset': 0,
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'lightgray': 37,
        'lightgrey': 37,
        'darkgray': 38,
        'darkgrey': 38,
        'lightred': 91,
        'lightgreen': 92,
        'lightyellow': 93,
        'lightblue': 94,
        'lightmagenta': 95,
        'lightcyan': 96,
        'white': 97
    }

    if color.lower() not in colors:
        return None
    return '\x1b[%sm' % colors[color.lower()]
