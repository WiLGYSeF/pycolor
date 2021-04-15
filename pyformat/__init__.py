from colorstate import ColorState
from pyformat import color
from pyformat import fieldsep


FORMAT_CHAR_VALID = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

FORMAT_COLOR = 'C'
FORMAT_FIELD = 'F'
FORMAT_GROUP = 'G'
FORMAT_PADDING = 'P'


def format_string(string, context=None, return_color_positions=False):
    if context is None:
        context = {}

    if 'color_state' in context:
        context['color_state_current'] = context['color_state'].copy()
    else:
        context['color_state_current'] = ColorState()

    context['past_color_states'] = [ context['color_state_current'].copy() ]

    newstring = ''
    color_positions = {}
    idx = 0
    last_format_idx = 0

    while idx < len(string):
        if string[idx] == '%':
            if idx + 1 < len(string) and string[idx + 1] == '%':
                newstring += '%'
                idx += 2
                continue

            formatter, value, newidx = get_formatter(string, idx)
            if formatter is not None:
                context['color_state_current'].set_state_by_string(newstring[last_format_idx:])

                result = do_format(string, formatter, value, idx, newidx, context)
                apppend_result = True

                if formatter == FORMAT_COLOR:
                    if return_color_positions:
                        color_positions[len(newstring)] = result
                        context['color_state_current'].set_state_by_string(result)
                        apppend_result = False

                last_format_idx = len(newstring)

                if apppend_result:
                    newstring += result

                idx = newidx
                continue

        newstring += string[idx]
        idx += 1

    if return_color_positions:
        return newstring, color_positions
    return newstring

def do_format(string, formatter, value, idx, newidx, context):
    if formatter == FORMAT_COLOR:
        if not context.get('color_enabled', True):
            return ''

        if value == 'prev':
            return get_lastcolor(
                context['past_color_states'],
                '2',
                current=context['color_state_current']
            )
        if value.startswith('last'):
            return get_lastcolor(
                context['past_color_states'],
                value[4:],
                current=context['color_state_current']
            )
        if value in ('s', 'soft'):
            return context['color_state_orig'].get_string(
                compare_state=context['color_state_current']
            )

        colorstr = color.get_color(
            value,
            aliases=context.get('color_aliases', {})
        )
        if colorstr is None:
            colorstr = ''

        newstate = context['past_color_states'][-1].copy()
        newstate.set_state_by_string(colorstr)
        context['past_color_states'].append(newstate)

        return colorstr

    if formatter == FORMAT_PADDING:
        pass

    if formatter == FORMAT_GROUP and 'match' in context:
        try:
            group = int(value)
        except ValueError:
            group = value

        try:
            matchgroup = context['match'][group]
        except IndexError:
            matchgroup = None

        if matchgroup is None:
            return ''
        return matchgroup

    if formatter == FORMAT_FIELD and 'fields' in context:
        return fieldsep.get_fields(value, context)

    return string[idx:newidx]

def get_formatter(string, idx):
    begin_idx = idx
    if idx >= len(string) or string[idx] != '%':
        return None, None, begin_idx

    idx += 1
    if idx >= len(string):
        return None, None, begin_idx

    formatter = None
    startidx = idx
    paren = -1

    while idx < len(string):
        if string[idx] not in FORMAT_CHAR_VALID:
            break
        idx += 1

    formatter = string[startidx:idx]
    if len(formatter) == 0:
        return None, None, begin_idx

    if idx < len(string) and string[idx] == '(':
        paren = 1
        idx += 1

    startidx = idx
    while idx < len(string):
        char = string[idx]
        if paren == 0:
            break
        if paren == -1 and char not in FORMAT_CHAR_VALID:
            break

        if char == '(':
            paren += 1
        elif char == ')':
            paren -= 1

        idx += 1

    if paren > 0:
        return None, None, begin_idx

    if paren == -1:
        if startidx == idx:
            value = formatter[1:]
            formatter = formatter[0]
        else:
            value = string[startidx:idx]
    else:
        value = string[startidx:idx - 1]

    return formatter, value, idx

def get_lastcolor(colors, string, current=None):
    if len(colors) == 0:
        return ''

    if current is None:
        current = ColorState()

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

    return colors[last_idx].get_string(compare_state=current)
