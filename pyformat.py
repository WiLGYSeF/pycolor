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

    # FIXME: should not decode here

    if 'match' in context:
        if formatter[0] == 'G':
            try:
                group = int(formatter[1:])
            except ValueError:
                group = formatter[1:]

            try:
                return context['match'][group].decode('utf-8')
            except IndexError:
                return ''
    if 'fields' in context:
        if formatter[0] == 'S':
            formatter = formatter[1:]
            last_field_num = fieldsep_idx_to_num(len(context['fields']))

            if formatter[0] == 'e':
                field_idx = int(formatter[1:])
                if field_idx < 0:
                    field_idx += last_field_num + 1
                field_idx = fieldsep_num_to_idx(field_idx - 1) + 1

                if field_idx >= len(context['fields']):
                    return ''
                return context['fields'][field_idx].decode('utf-8')

            indexes = set()

            comma_idx = formatter.find(',')
            if comma_idx != -1:
                number = formatter[:comma_idx]
                sep = formatter[comma_idx + 1:].encode('utf-8')
            else:
                number = formatter
                sep = None

            if '*' in number:
                rangespl = number.split('*')
                start = rangespl[0]
                end = rangespl[1]

                if len(start) == 0:
                    start = fieldsep_num_to_idx(1)
                else:
                    start = fieldsep_num_to_idx(int(start))

                if len(end) == 0:
                    end = len(context['fields'])
                else:
                    end = int(end)
                    if end < 0:
                        end += last_field_num + 1
                    end = fieldsep_num_to_idx(end)

                for i in range(start, end + 1):
                    indexes.add(i)
            else:
                number = int(number)
                if number < 0:
                    number += last_field_num + 1
                indexes.add(fieldsep_num_to_idx(number))

            indexes = sorted(indexes)
            if len(indexes) == 0:
                return ''

            newstring = context['fields'][indexes[0]]

            for i in range(2, len(indexes), 2):
                if indexes[i] >= len(context['fields']):
                    break

                if sep is None:
                    newstring += context['fields'][indexes[i - 1]] + context['fields'][indexes[i]]
                else:
                    newstring += sep + context['fields'][indexes[i]]

            return newstring.decode('utf-8')

    return string[idx:newidx]

def fieldsep_idx_to_num(idx):
    return idx // 2 + 1

def fieldsep_num_to_idx(num):
    return (num - 1) * 2

def get_formatter(string, idx):
    if idx >= len(string) or string[idx] != '%':
        return None, idx

    idx += 1

    if idx >= len(string):
        return None, idx

    paren = 0
    first_char_before_paren = False

    if string[idx] == '(':
        paren = 1
        idx += 1
    elif string[idx + 1] == '(' and string[idx] in FORMAT_CHAR_VALID:
        first_char_before_paren = True
        paren = 1
        idx += 2

    startidx = idx

    while idx < len(string):
        char = string[idx]
        if paren != 1 and char not in FORMAT_CHAR_VALID:
            break

        if paren == 1 and char == ')':
            paren = -1
            idx += 1
            break

        idx += 1

    if paren == -1:
        if first_char_before_paren:
            formatter = string[startidx - 2] + string[startidx:idx - 1]
        else:
            formatter = string[startidx:idx - 1]
    else:
        formatter = string[startidx:idx]

    return formatter, idx

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
