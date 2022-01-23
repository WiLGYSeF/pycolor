import re
import typing

from . import fieldsep
from .coloring import ColorPositions
from .coloring.colorpositions import (
    insert_color_data,
    offset_color_positions,
    update_color_positions
)
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

class Formatter:
    def __init__(self, context: typing.Optional[Context] = None):
        self._context: Context = context if context is not None else Context()

        self._cur_newstring: str = ''
        self._cur_color_positions: ColorPositions = {}

    def format_string(self, string: str) -> typing.Tuple[str, ColorPositions]:
        """Formats string

        Args:
            string (str): Format string

        Returns:
            tuple: Formatted string and color positions dict
        """
        self._cur_newstring = ''
        self._cur_color_positions = {}
        last = 0

        def parse(string: str) -> str:
            return string.replace('%%', '%')

        for match in FORMAT_REGEX.finditer(string):
            self._cur_newstring += parse(string[last:match.start()])

            formatter, param = get_format_param(match)
            if formatter is not None:
                result = self._do_format(
                    formatter,
                    param if param is not None else ''
                )
                if result is not None:
                    if formatter in FORMAT_COLOR:
                        newstrlen = len(self._cur_newstring)
                        if newstrlen not in self._cur_color_positions:
                            self._cur_color_positions[newstrlen] = ''
                        self._cur_color_positions[newstrlen] += result
                    else:
                        self._cur_newstring += result

            last = match.end()
        self._cur_newstring += parse(string[last:])

        return self._cur_newstring, self._cur_color_positions

    def fmt_str(self, string: str) -> str:
        """Format string

        Args:
            string (str): Format string

        Returns:
            str: Formatted string
        """
        newstring, color_positions = self.format_string(string)
        return insert_color_data(newstring, color_positions)

    def copy(self) -> 'Formatter':
        """Copies the formatter

        Returns:
            Formatter: Copied formatter
        """
        return Formatter(context=self._context.copy())

    def _do_format(self, formatter: str, value: str) -> typing.Optional[str]:
        if formatter in FORMAT_COLOR:
            return self._do_format_color(value)
        if formatter in FORMAT_FIELD:
            return self._do_format_field(value) if self._context.fields is not None else ''
        if formatter in FORMAT_GROUP:
            return self._do_format_group(value) if self._context.match is not None else ''
        if formatter in FORMAT_CONTEXT_COLOR:
            if self._context.match is not None and self._context.match_cur is not None:
                return self._do_format_field_group_color(value, '%Gc')
            if self._context.field_cur is not None:
                return self._do_format_field_group_color(value, '%Fc')
            return ''
        if formatter in FORMAT_PADDING:
            return self._do_format_padding(value)
        if formatter in FORMAT_TRUNCATE:
            return self._do_format_truncate(value)
        return None

    def _do_format_color(self, value: str) -> str:
        if not self._context.color_enabled:
            return ''

        def get_state(context: Context) -> ColorState:
            return ColorState(insert_color_data(
                '',
                context.color_positions,
                context.color_positions_end_idx + 1
            ))

        if value == 'prev':
            prev = str(get_state(self._context))
            return prev if len(prev) != 0 else '\x1b[0m'
        if value in ('s', 'soft'):
            curstate = get_state(self._context)
            curstate.set(insert_color_data(self._cur_newstring, self._cur_color_positions))
            return ColorState().get_string(compare_state=curstate)

        colorstr = color.get_color(value, aliases=self._context.color_aliases)
        return colorstr if colorstr is not None else ''

    def _do_format_field(self, value: str) -> str:
        if value == 'c' and self._context.field_cur is not None:
            return self._context.field_cur
        return fieldsep.get_fields(value, self._context.fields)

    def _do_format_group(self, value: str) -> str:
        group: typing.Union[str, int] = -1

        try:
            group = int(value)
            self._context.match_incr = group + 1
        except ValueError:
            group = value

        if self._context.match is not None:
            try:
                matchgroup = self._context.match[group]
                return matchgroup if matchgroup else ''
            except IndexError:
                pass

        if self._context.match_cur is not None and group == 'c':
            return self._context.match_cur
        if self._context.match is not None and group == 'n':
            try:
                if self._context.match_incr is not None:
                    matchgroup = self._context.match[self._context.match_incr]
                    self._context.match_incr += 1
                else:
                    matchgroup = self._context.match[1]
                    self._context.match_incr = 2
                return matchgroup if matchgroup else ''
            except IndexError:
                pass
        return ''

    def _do_format_field_group_color(self, value: str, format_type: str) -> str:
        copy = self.copy()
        result, color_pos = copy.format_string(f'%C({value}){format_type}%Cz')
        update_color_positions(
            self._cur_color_positions,
            offset_color_positions(color_pos, len(self._cur_newstring))
        )
        return result

    def _do_format_padding(self, value: str) -> str:
        value_sep = value.find(';')
        if value_sep != -1:
            try:
                spl = value[:value_sep].split(',')
                padcount = int(spl[0])
                padchar = ' ' if len(spl) == 1 else spl[1][0]

                value = value[value_sep + 1:]

                copy = self.copy()
                copy._context.color_enabled = False
                newstring, _ = copy.format_string(value)
                result = padchar * (padcount - len(newstring))
                return result
            except ValueError:
                pass
        return ''

    def _do_format_truncate(self, value: str) -> str:
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

        copy = self.copy()
        copy._context.color_enabled = False
        string = copy.fmt_str(string)

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

def fmt_str(string: str, color_enabled: bool = True) -> str:
    formatter = Formatter(
        context=Context(
            color_enabled=color_enabled
        )
    )
    return formatter.fmt_str(string)

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
