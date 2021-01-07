from pyformat import color
from pyformat import fieldsep


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
        colorstr = color.get_color(formatter[1:])
        return colorstr if colorstr is not None else ''

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
            return fieldsep.get_fields(formatter[1:], context)

    return string[idx:newidx]

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