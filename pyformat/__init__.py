from pyformat import color
from pyformat import fieldsep


FORMAT_CHAR_VALID = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

FORMAT_COLOR = 'C'
FORMAT_FIELD = 'F'
FORMAT_GROUP = 'G'


def format_string(string, context=None, return_color_positions=False):
    if context is None:
        context = {}

    context['last_colors'] = []

    newstring = ''
    color_positions = {}
    idx = 0

    while idx < len(string):
        if string[idx] == '%':
            if idx + 1 < len(string) and string[idx + 1] == '%':
                newstring += '%'
                idx += 2
                continue

            formatter, newidx = get_formatter(string, idx)
            if formatter is not None:
                result = do_format(string, formatter, idx, newidx, context)
                apppend_result = True

                if is_color_format(formatter):
                    if return_color_positions:
                        color_positions[len(newstring)] = result
                        apppend_result = False

                if apppend_result:
                    newstring += result
                idx = newidx
                continue

        newstring += string[idx]
        idx += 1

    if return_color_positions:
        return newstring, color_positions

    return newstring

def do_format(string, formatter, idx, newidx, context):
    if is_color_format(formatter):
        if not context.get('color_enabled', True):
            return ''

        if formatter[1:].lower() == 'prev':
            return get_lastcolor(context['last_colors'], '2')
        if formatter[1:].lower().startswith('last'):
            return get_lastcolor(context['last_colors'], formatter[5:])

        colorstr = color.get_color(
            formatter[1:],
            aliases=context.get('color_aliases', {})
        )
        if colorstr is None:
            colorstr = ''

        context['last_colors'].append(colorstr)
        return colorstr

    if 'match' in context:
        if formatter[0] == FORMAT_GROUP:
            try:
                group = int(formatter[1:])
            except ValueError:
                group = formatter[1:]

            try:
                return context['match'][group]
            except IndexError:
                return ''
    if 'fields' in context:
        if formatter[0] == FORMAT_FIELD:
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
    elif idx + 1 < len(string) and string[idx + 1] == '(' and string[idx] in FORMAT_CHAR_VALID:
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

def is_color_format(string):
    return string[0] == 'C'

def get_lastcolor(colors, string):
    if len(colors) == 0:
        return ''

    try:
        last_idx = -int(string)
    except ValueError:
        last_idx = -1

    if last_idx >= 0:
        last_idx -= 1
        if last_idx >= len(colors):
            last_idx = -1
    elif -last_idx > len(colors):
        last_idx = 0

    return colors[last_idx]
