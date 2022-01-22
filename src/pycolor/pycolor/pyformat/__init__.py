import re
import typing

from . import fieldsep
from .coloring.colorpositions import insert_color_data
from .coloring.colorstate import ColorState
from .coloring import color
from .context import Context

FORMAT_REGEX = re.compile(''.join([
    '(?<!%)%(?:',
        r'\((?P<format0>[A-Za-z0-9]+)(?::(?P<param0>[^()]*))?\)',
        '|',
        r'(?P<format1>[A-Za-z])\((?P<param1>[^()]+)\)',
        '|',
        r'(?P<format2>[A-Za-z])(?P<param2>[A-Za-z0-9]+)?'
    ')'
]))

FORMAT_COLOR = ('color', 'C')
FORMAT_FIELD = ('field', 'F')
FORMAT_GROUP = ('group', 'G')
FORMAT_CONTEXT_COLOR = ('colorctx', 'H')
FORMAT_PADDING = ('pad', 'P')
FORMAT_TRUNCATE = ('trunc', 'T')

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
    last = 0

    def parse(string: str) -> str:
        return string.replace('%%', '%')

    for match in FORMAT_REGEX.finditer(string):
        newstring += parse(string[last:match.start()])

        formatter, param = get_format_param(match)
        if formatter is not None and param is not None:
            result = _do_format(
                formatter,
                param,
                context,
                newstring=newstring,
                color_positions=color_positions,
            )

            if result is not None:
                if formatter in FORMAT_COLOR:
                    newstrlen = len(newstring)
                    if newstrlen not in color_positions:
                        color_positions[newstrlen] = ''
                    color_positions[newstrlen] += result
                else:
                    newstring += result
        last = match.end()
    newstring += parse(string[last:])

    return newstring, color_positions

def get_format_param(match: re.Match) -> typing.Tuple[
    typing.Optional[str],
    typing.Optional[str]
]:
    return (
        _get_numbered_group(match, 'format'),
        _get_numbered_group(match, 'param')
    )

def _get_numbered_group(match: re.Match, name: str, start: int = 0) -> typing.Optional[str]:
    groups = match.groupdict()
    idx = start

    while True:
        key = f'{name}{idx}'
        if key not in groups:
            return None
        if groups[key] is not None:
            return groups[key]
        idx += 1
    return None

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
    if formatter in FORMAT_COLOR:
        return _do_format_color(value, context, **kwargs)
    if formatter in FORMAT_FIELD:
        return _do_format_field(value, context, **kwargs) if context.fields is not None else ''
    if formatter in FORMAT_GROUP:
        return _do_format_group(value, context, **kwargs) if context.match is not None else ''
    if formatter in FORMAT_CONTEXT_COLOR:
        if context.match is not None and context.match_cur is not None:
            return _do_format_field_group_color(value, context, '%Gc', **kwargs)
        if context.field_cur is not None:
            return _do_format_field_group_color(value, context, '%Fc', **kwargs)
        return ''
    if formatter in FORMAT_PADDING:
        return _do_format_padding(value, context, **kwargs)
    if formatter in FORMAT_TRUNCATE:
        return _do_format_truncate(value, context, **kwargs)
    return None

def _do_format_color(value: str, context: Context, **kwargs) -> str:
    if not context.color_enabled:
        return ''

    def get_state(context: Context) -> ColorState:
        return ColorState(insert_color_data(
            '',
            context.color_positions,
            context.color_positions_end_idx + 1
        ))

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
