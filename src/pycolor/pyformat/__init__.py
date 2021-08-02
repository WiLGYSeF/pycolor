from ..colorpositions import insert_color_data
from ..colorstate import ColorState
from . import color
from . import fieldsep


FORMAT_CHAR_VALID = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

FORMAT_COLOR = 'C'
FORMAT_FIELD = 'F'
FORMAT_GROUP = 'G'
FORMAT_CONTEXT_COLOR = 'H'
FORMAT_PADDING = 'P'
FORMAT_TRUNCATE = 'T'


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
                    formatter,
                    value,
                    context,
                    newstring=newstring,
                    color_positions=color_positions,
                )
                if result is None:
                    result = string[idx:newidx]

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

def do_format(formatter, value, context, **kwargs):
    if formatter == FORMAT_COLOR:
        return do_format_color(value, context, **kwargs)
    if formatter == FORMAT_FIELD:
        if 'fields' not in context:
            return ''
        return do_format_field(value, context, **kwargs)
    if formatter == FORMAT_GROUP:
        if 'match' not in context:
            return ''
        return do_format_group(value, context, **kwargs)
    if formatter == FORMAT_CONTEXT_COLOR:
        if 'match' in context and 'match_cur' in context:
            return do_format_field_group_color(value, context, '%Gc',**kwargs)
        if 'field_cur' in context:
            return do_format_field_group_color(value, context, '%Fc', **kwargs)
        return ''
    if formatter == FORMAT_PADDING:
        return do_format_padding(value, context, **kwargs)
    if formatter == FORMAT_TRUNCATE:
        return do_format_truncate(value, context, **kwargs)
    return None

def do_format_color(value, context, **kwargs):
    ctx = context.get('color', {})
    if not ctx.get('enabled', True):
        return ''

    def get_state(context):
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

    if value == 'prev':
        prev = str(get_state(context))
        return prev if len(prev) != 0 else '\x1b[0m'
    if value in ('s', 'soft'):
        newstring = kwargs.get('newstring', None)
        color_positions = kwargs.get('color_positions', {})

        curstate = get_state(context)
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

def do_format_field(value, context, **kwargs):
    if value == 'c' and 'field_cur' in context:
        return context['field_cur']
    return fieldsep.get_fields(value, context)

def do_format_group(value, context, **kwargs):
    try:
        group = int(value)
        context['match_incr'] = group + 1
    except ValueError:
        group = value

    try:
        matchgroup = context['match'][group]
        return matchgroup if matchgroup else ''
    except IndexError:
        pass

    if 'match_cur' in context and group == 'c':
        return context['match_cur']
    if group == 'n':
        if 'match_incr' not in context:
            context['match_incr'] = 1
        try:
            matchgroup = context['match'][context['match_incr']]
            context['match_incr'] += 1
            return matchgroup if matchgroup else ''
        except IndexError:
            pass
    return ''

def do_format_field_group_color(value, context, format_type, **kwargs):
    result, color_pos = format_string(
        '%C(' + value + ')' + format_type + '%Cz',
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

def do_format_padding(value, context, **kwargs):
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

def do_format_truncate(value, context, **kwargs):
    str_loc_sep = value.rfind(';')
    string_repl = value[:str_loc_sep]
    location, length = value[str_loc_sep + 1:].split(',')

    rev_string_repl = ''
    string_repl_sep = len(string_repl)
    i = len(string_repl) - 1
    while i >= 0:
        if i > 0 and string_repl[i - 1] == '\\':
            rev_string_repl += string_repl[i]
            i -= 2
            continue
        if string_repl[i] == ';':
            string_repl_sep = i
            rev_string_repl += string_repl[:i + 1][::-1]
            break
        rev_string_repl += string_repl[i]
        i -= 1

    string_repl = rev_string_repl[::-1]
    string = string_repl[:string_repl_sep]
    repl = string_repl[string_repl_sep + 1:]

    location = location.lower()
    length = int(length)
    if length <= 0:
        raise ValueError('invalid length: %d' % length)

    if 'color' in context:
        context = dictcopy(context)
        context['color']['enabled'] = False
    string = format_string(string, context=context)

    if location in ('start', 's'):
        if len(string) > length:
            length -= len(repl)
            string = repl + string[-length:]
    elif location in ('start-add', 'sa'):
        if len(string) > length:
            string = repl + string[-length:]
    elif location in ('mid', 'm'):
        if len(string) > length:
            length -= len(repl)
            half = length // 2
            string = string[:half] + repl + string[-(length - half):]
    elif location in ('mid-add', 'ma'):
        if len(string) > length:
            half = length // 2
            string = string[:half] + repl + string[-(length - half):]
    elif location in ('end', 'e'):
        if len(string) > length:
            length -= len(repl)
            string = string[:length] + repl
    elif location in ('end-add', 'ea'):
        if len(string) > length:
            string = string[:length] + repl
    else:
        raise ValueError('invalid truncate location: %s' % location)
    return string

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

def dictcopy(dct):
    copy = {}
    for key, val in dct.items():
        if isinstance(val, dict):
            copy[key] = dictcopy(val)
        else:
            copy[key] = val
    return copy
