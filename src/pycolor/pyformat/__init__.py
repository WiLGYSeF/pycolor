import typing

from ..colorpositions import insert_color_data
from ..colorstate import ColorState
from . import color
from .context import Context
from . import fieldsep

FORMAT_CHAR_VALID = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

FORMAT_COLOR = 'C'
FORMAT_FIELD = 'F'
FORMAT_GROUP = 'G'
FORMAT_CONTEXT_COLOR = 'H'
FORMAT_PADDING = 'P'
FORMAT_TRUNCATE = 'T'

def format_string(
    string: str,
    context: Context = None
) -> typing.Tuple[str, typing.Dict[int, str]]:
    """Formats string

    Args:
        string (str): Format string
        context (Context): Context

    Returns:
        tuple: Formatted string and color positions dict
    """
    if context is None:
        context = Context()

    newstring = ''
    color_positions: typing.Dict[int, str] = {}
    idx = 0

    strlen = len(string)
    while idx < strlen:
        if string[idx] == '%':
            if idx + 1 < strlen and string[idx + 1] == '%':
                newstring += '%'
                idx += 2
                continue

            formatter, value, newidx = get_formatter(string, idx)
            if formatter is not None and value is not None:
                result = _do_format(
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

    return newstring, color_positions

def fmt_str(
    string: str,
    context: Context = None
) -> str:
    """Format string

    Args:
        string (str): Format string
        context (Context): Context

    Returns:
        str: Formatted string
    """
    newstring, color_positions = format_string(string, context)
    return insert_color_data(newstring, color_positions)

def _do_format(formatter: str, value: str, context: Context, **kwargs) -> typing.Optional[str]:
    if formatter == FORMAT_COLOR:
        return _do_format_color(value, context, **kwargs)
    if formatter == FORMAT_FIELD:
        return _do_format_field(value, context, **kwargs) if context.fields is not None else ''
    if formatter == FORMAT_GROUP:
        return _do_format_group(value, context, **kwargs) if context.match is not None else ''
    if formatter == FORMAT_CONTEXT_COLOR:
        if context.match is not None and context.match_cur is not None:
            return _do_format_field_group_color(value, context, '%Gc', **kwargs)
        if context.field_cur is not None:
            return _do_format_field_group_color(value, context, '%Fc', **kwargs)
        return ''
    if formatter == FORMAT_PADDING:
        return _do_format_padding(value, context, **kwargs)
    if formatter == FORMAT_TRUNCATE:
        return _do_format_truncate(value, context, **kwargs)
    return None

def _do_format_color(value: str, context: Context, **kwargs) -> str:
    if not context.color_enabled:
        return ''

    def get_state(context: Context) -> ColorState:
        state = context.color_state if context.color_state else ColorState()

        if context.string is not None and context.string_idx is not None:
            state.set(
                insert_color_data(
                    context.string,
                    context.color_positions,
                    context.string_idx
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
            curstate.set(insert_color_data(newstring, color_positions))
        return ColorState().get_string(compare_state=curstate)

    colorstr = color.get_color(value, aliases=context.color_aliases)
    return colorstr if colorstr is not None else ''

def _do_format_field(value: str, context: Context, **kwargs) -> str:
    if value == 'c' and context.field_cur is not None:
        return context.field_cur
    return fieldsep.get_fields(value, context)

def _do_format_group(value: str, context: Context, **kwargs) -> str:
    group: typing.Union[str, int] = -1

    try:
        group = int(value)
        context.match_incr = group + 1
    except ValueError:
        group = value

    if context.match is not None:
        try:
            matchgroup = context.match[group]
            return matchgroup if matchgroup else ''
        except IndexError:
            pass

    if context.match_cur is not None and group == 'c':
        return context.match_cur
    if context.match is not None and group == 'n':
        try:
            if context.match_incr is not None:
                matchgroup = context.match[context.match_incr]
                context.match_incr += 1
            else:
                matchgroup = context.match[1]
                context.match_incr = 2
            return matchgroup if matchgroup else ''
        except IndexError:
            pass
    return ''

def _do_format_field_group_color(value: str, context: Context, format_type: str, **kwargs) -> str:
    result, color_pos = format_string(
        '%C(' + value + ')' + format_type + '%Cz',
        context=context
    )
    if 'color_positions' in kwargs:
        color_positions = kwargs['color_positions']
        offset = len(kwargs.get('newstring', ''))
        for pos, val in color_pos.items():
            color_positions[pos + offset] = val
        return result
    return insert_color_data(result, color_pos)

def _do_format_padding(value: str, context: Context, **kwargs) -> str:
    value_sep = value.find(';')
    if value_sep != -1:
        try:
            spl = value[:value_sep].split(',')
            padcount = int(spl[0])
            padchar = ' ' if len(spl) == 1 else spl[1][0]

            value = value[value_sep + 1:]

            context = context.copy()
            context.color_enabled = False

            return padchar * (padcount - len(fmt_str(value, context=context)))
        except ValueError:
            pass
    return ''

def _do_format_truncate(value: str, context: Context, **kwargs) -> str:
    str_loc_sep = value.rfind(';')
    string_repl = value[:str_loc_sep]
    location, length_str = value[str_loc_sep + 1:].split(',')

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
    length = int(length_str)
    if length <= 0:
        raise ValueError('invalid length: %d' % length)

    context = context.copy()
    context.color_enabled = False
    string = fmt_str(string, context=context)

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

def get_formatter(
    string: str,
    idx: int
) -> typing.Tuple[
    typing.Optional[str],
    typing.Optional[str],
    int
]:
    """Gets the formatter and value at index

    Args:
        string (str): Format string
        idx (int): Start index

    Returns:
        tuple: Formatter, value, and end index
    """
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
