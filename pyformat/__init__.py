from colorpositions import insert_color_data
from colorstate import ColorState
from pyformat import color
from pyformat import fieldsep


FORMAT_CHAR_VALID = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

FORMAT_COLOR = 'C'
FORMAT_FIELD = 'F'
FORMAT_GROUP = 'G'
FORMAT_GROUP_COLOR = 'H'
FORMAT_PADDING = 'P'


def format_string(string, context=None, return_color_positions=False):
    if context is None:
        context = {}

    newstring = ''
    color_positions = {}
    idx = 0

    strlen = len(string)
    while idx < strlen:
        if string[idx] == '%':
            if idx + 1 < strlen and string[idx + 1] == '%':
                newstring += '%'
                idx += 2
                continue

            formatter, value, newidx = get_formatter(string, idx)
            if formatter is not None:
                result = do_format(
                    string,
                    formatter,
                    value,
                    idx,
                    newidx,
                    context,
                    newstring=newstring,
                    color_positions=color_positions,
                )
                if formatter == FORMAT_COLOR:
                    newstrlen = len(newstring)
                    if newstrlen not in color_positions:
                        color_positions[newstrlen] = ''
                    color_positions[newstrlen] += result
                else:
                    newstring += result

                idx = newidx
                continue

        newstring += string[idx]
        idx += 1

    if return_color_positions:
        return newstring, color_positions
    return insert_color_data(newstring, color_positions)

def do_format(string, formatter, value, idx, newidx, context, **kwargs):
    if formatter == FORMAT_COLOR:
        ctx = context.get('color', {})
        if not ctx.get('enabled', True):
            return ''

        if value == 'prev':
            prev = str(_get_state(context))
            return prev if len(prev) != 0 else '\x1b[0m'
        if value in ('s', 'soft'):
            newstring = kwargs.get('newstring', None)
            color_positions = kwargs.get('color_positions', {})

            curstate = _get_state(context)
            if newstring is not None:
                curstate.set_state_by_string(
                    insert_color_data(newstring, color_positions)
                )
            return ColorState().get_string(
                compare_state=curstate
            )

        colorstr = color.get_color(
            value,
            aliases=ctx.get('aliases', {})
        )
        if colorstr is None:
            colorstr = ''
        return colorstr

    if formatter == FORMAT_PADDING:
        value_sep = value.find(';')
        if value_sep != -1:
            try:
                spl = value[0:value_sep].split(',')
                padcount = int(spl[0])
                padchar = ' ' if len(spl) == 1 else spl[1][0]

                value = value[value_sep + 1:]

                if 'color' in context:
                    context = dictcopy(context)
                    context['color']['enabled'] = False

                return padchar * (padcount - len(format_string(value, context=context)))
            except ValueError:
                pass
        return ''

    if 'match' in context:
        if formatter == FORMAT_GROUP:
            if value == 'c' and 'match_cur' in context:
                return context['match_cur']

            try:
                group = int(value)
                context['match_incr'] = group + 1
            except ValueError:
                group = value

            try:
                matchgroup = context['match'][group]
            except IndexError:
                matchgroup = None

            if matchgroup is None and group == 'n':
                if 'match_incr' not in context:
                    context['match_incr'] = 1

                try:
                    matchgroup = context['match'][context['match_incr']]
                    context['match_incr'] += 1
                    return matchgroup
                except IndexError:
                    pass
            return matchgroup if matchgroup else ''
        if formatter == FORMAT_GROUP_COLOR and 'match_cur' in context:
            result, color_pos = format_string(
                '%C' + value + '%Gc%Cz',
                context=context,
                return_color_positions=True
            )
            if 'color_positions' in kwargs:
                color_positions = kwargs['color_positions']
                offset = len(kwargs.get('newstring', ''))
                for pos, val in color_pos.items():
                    color_positions[pos + offset] = val
                return result
            return insert_color_data(result, color_pos)

    if formatter == FORMAT_FIELD and 'fields' in context:
        if value == 'c' and 'field_cur' in context:
            return context['field_cur']
        return fieldsep.get_fields(value, context)

    return string[idx:newidx]

def get_formatter(string, idx):
    strlen = len(string)
    begin_idx = idx

    if idx >= strlen - 1 or string[idx] != '%':
        return None, None, begin_idx
    idx += 1

    formatter = None
    startidx = idx
    paren = -1

    while idx < strlen:
        if string[idx] not in FORMAT_CHAR_VALID:
            break
        idx += 1

    formatter = string[startidx:idx]
    if len(formatter) == 0:
        return None, None, begin_idx

    if idx != strlen and string[idx] == '(':
        paren = 1
        idx += 1

        startidx = idx
        while idx < strlen:
            char = string[idx]
            if paren == 0:
                break
            if char == '\\':
                idx += 2
                continue

            if char == '(':
                paren += 1
            elif char == ')':
                paren -= 1

            idx += 1

        if paren > 0:
            return None, None, begin_idx

        value = string[startidx:idx - 1]
        formatter = formatter[:startidx]
    else:
        value = formatter[1:idx - 1]
        formatter = formatter[:1]

    return formatter, value, idx

def _get_state(context):
    ctx_color = context.get('color', {})
    state = ctx_color['state'] if 'state' in ctx_color else ColorState()

    if 'string' in context:
        state.set_state_by_string(
            insert_color_data(
                context['string'],
                ctx_color.get('positions', {}),
                context['idx']
            )
        )
    return state

def dictcopy(dct):
    copy = {}
    for key, val in dct.items():
        if isinstance(val, dict):
            copy[key] = dictcopy(val)
        else:
            copy[key] = val
    return copy
