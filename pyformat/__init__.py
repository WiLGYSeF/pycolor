from colorpositions import insert_color_data
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
    if 'color' not in context:
        context['color'] = {}
    ctx_color = context['color']

    if ctx_color.get('enabled', True):
        if 'state' not in ctx_color:
            ctx_color['state'] = ColorState()
        ctx_color['state_current'] = ctx_color['state'].copy()
        if 'past_states' not in ctx_color or len(ctx_color['past_states']) == 0:
            ctx_color['past_states'] = [ ctx_color['state'].copy() ]

    newstring = ''
    color_positions = {}
    idx = 0

    while idx < len(string):
        if string[idx] == '%':
            if idx + 1 < len(string) and string[idx + 1] == '%':
                newstring += '%'
                idx += 2
                continue

            formatter, value, newidx = get_formatter(string, idx)
            if formatter is not None:
                if ctx_color.get('enabled', True):
                    ctx_color['state_current'].reset()
                    ctx_color['state_current'].set_state_by_string(
                        insert_color_data(newstring, color_positions)
                    )

                result = do_format(string, formatter, value, idx, newidx, context)
                if formatter == FORMAT_COLOR:
                    if len(newstring) not in color_positions:
                        color_positions[len(newstring)] = ''
                    color_positions[len(newstring)] += result
                else:
                    newstring += result

                idx = newidx
                continue

        newstring += string[idx]
        idx += 1

    if return_color_positions:
        return newstring, color_positions
    return insert_color_data(newstring, color_positions)

def do_format(string, formatter, value, idx, newidx, context):
    if formatter == FORMAT_COLOR:
        ctx = context.get('color', {})
        if not ctx.get('enabled', True):
            return ''

        if value == 'prev':
            return get_lastcolor(
                ctx['past_states'],
                '2',
                current=ctx['state_current']
            )
        if value.startswith('last'):
            return get_lastcolor(
                ctx['past_states'],
                value[4:],
                current=ctx['state_current']
            )
        if value in ('s', 'soft'):
            state = ctx['state'].copy()
            if 'positions' in ctx:
                state.set_state_by_string(
                    insert_color_data(
                        context['string'],
                        ctx['positions'],
                        context['idx']
                    )
                )

            return state.get_string(
                compare_state=ctx['state_current']
            )

        colorstr = color.get_color(
            value,
            aliases=ctx.get('aliases', {})
        )
        if colorstr is None:
            colorstr = ''

        newstate = ctx['past_states'][-1].copy()
        newstate.set_state_by_string(colorstr)
        ctx['past_states'].append(newstate)

        return colorstr

    if formatter == FORMAT_PADDING:
        value_sep = value.find(';')
        if value_sep != -1:
            try:
                spl = value[0:value_sep].split(',')
                padcount = int(spl[0])
                padchar = ' ' if len(spl) == 1 else spl[1][0]

                value = value[value_sep + 1:]

                newctx = dictcopy(context)
                newctx['color']['enabled'] = False

                return padchar * (padcount - len(format_string(value, context=newctx)))
            except ValueError:
                pass
        return ''

    if formatter == FORMAT_GROUP and 'match' in context:
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

    if formatter == FORMAT_FIELD and 'fields' in context:
        if value == 'c' and 'field_cur' in context:
            return context['field_cur']

        return fieldsep.get_fields(value, context)

    return string[idx:newidx]

def get_formatter(string, idx):
    begin_idx = idx
    if idx >= len(string) - 1 or string[idx] != '%':
        return None, None, begin_idx
    idx += 1

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
        if paren <= 0:
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

def dictcopy(dct):
    copy = {}
    for key, val in dct.items():
        if isinstance(val, dict):
            copy[key] = dictcopy(val)
        else:
            copy[key] = val
    return copy
