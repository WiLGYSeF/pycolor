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
        r'\((?P<format0>[A-Za-z0-9]+)(?::(?P<param0>(?:[^()]|\\\(|\\\))*))?\)',
        '|',
        r'(?P<format1>[A-Za-z])\((?P<param1>(?:[^()]|\\\(|\\\))+)\)',
        '|',
        r'(?P<format2>[A-Za-z])(?P<param2>[A-Za-z0-9]+)?'
    ')'
]))

FORMAT_ALIGN = ('align', )
FORMAT_TRUNCATE = ('trunc', )
FORMAT_END = ('end', )

FORMAT_COLOR = ('color', 'C')
FORMAT_FIELD = ('field', 'F')
FORMAT_GROUP = ('group', 'G')
FORMAT_CONTEXT_COLOR = ('colorctx', 'H')

LEFT = 'left'
MIDDLE = 'middle'
RIGHT = 'right'

class Formatter:
    def __init__(self, context: typing.Optional[Context] = None):
        self._context: Context = context if context is not None else Context()

        self._cur_newstring: str = ''
        self._cur_color_positions: ColorPositions = {}
        self._cur_nested_state: dict = {}
        self._next_nested_state: dict = {}

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
            if match.end() <= last:
                # was already handled by recursive format
                continue

            self._cur_newstring += parse(string[last:match.start()])

            formatter, param = get_format_param(match)
            if formatter is not None:
                if formatter in FORMAT_END and len(self._cur_nested_state) != 0:
                    # end of the recursive format
                    last = match.end()
                    break

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
                else:
                    if len(self._next_nested_state) != 0:
                        # do a recursive format with the state passed
                        copy, result = self._recursive_format(string[match.end():])
                        self._cur_newstring += result
                        # jump to the end of the recursive format
                        last = match.end() + copy._cur_nested_state['last_index']
                        continue

            last = match.end()

        if len(self._cur_nested_state) != 0:
            self._cur_newstring = self._do_state_format()
            self._cur_nested_state['last_index'] = last
        else:
            self._cur_newstring += parse(string[last:])

        return self._cur_newstring, self._cur_color_positions.copy()

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
        copy = Formatter(context=self._context.copy())
        copy._cur_nested_state = self._next_nested_state.copy()
        return copy

    def _recursive_format(self, string: str) -> typing.Tuple['Formatter', str]:
        copy = self.copy()
        newstring, colorpos = copy.format_string(string)
        update_color_positions(
            self._cur_color_positions,
            offset_color_positions(colorpos, len(self._cur_newstring))
        )
        return copy, newstring

    def _do_format(self, formatter: str, value: str) -> typing.Optional[str]:
        if formatter in FORMAT_ALIGN:
            self._prepare_format_align(value)
            return None
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
        if formatter in FORMAT_TRUNCATE:
            self._prepare_format_truncate(value)
            return None
        return None

    def _do_state_format(self) -> str:
        format_type = self._cur_nested_state['type']
        if format_type in FORMAT_ALIGN:
            return self._do_format_align(
                self._cur_newstring,
                self._cur_nested_state['width'],
                self._cur_nested_state['position'],
                self._cur_nested_state['padchar']
            )
        if format_type in FORMAT_TRUNCATE:
            return self._do_format_truncate(
                self._cur_newstring,
                self._cur_nested_state['length'],
                self._cur_nested_state['location'],
                self._cur_nested_state['replace'],
                self._cur_nested_state['hard_length'],
            )
        return ''

    def _prepare_format_align(self, value: str) -> None:
        try:
            spl = value.split(',')
            width = int(spl[0])
            position = spl[1].lower() if len(spl) > 1 else LEFT
            padchar = spl[2][0] if len(spl) > 2 else ' '

            if position not in [LEFT, MIDDLE, RIGHT]:
                position = LEFT

            self._next_nested_state = {
                'type': 'align',
                'width': width,
                'position': position,
                'padchar': padchar
            }
        except ValueError:
            pass

    def _prepare_format_truncate(self, value: str) -> None:
        try:
            # split by comma, but allow escaping commas for replace string
            spl = re.split(r'(?<!\\),', value)
            length = int(spl[0])
            location = spl[1].lower()
            replace = spl[2].replace(r'\,', ',') if len(spl) > 2 else ''
            hard_length = spl[3].lower() if len(spl) > 3 else 'yes'

            if location not in [LEFT, MIDDLE, RIGHT]:
                location = LEFT

            self._next_nested_state = {
                'type': 'trunc',
                'length': length,
                'location': location,
                'replace': replace,
                'hard_length': hard_length == 'yes'
            }
        except ValueError:
            pass

    def _do_format_align(self, value: str, width: int, position: str, padchar: str) -> str:
        diff = width - len(value)
        if diff <= 0:
            return value

        result = ''
        if position == LEFT:
            result = value + (padchar * diff)
        elif position == MIDDLE:
            half = diff // 2
            result = (padchar * half) + value + (padchar * (diff - half))
        elif position == RIGHT:
            result = (padchar * diff) + value
        return result

    def _do_format_color(self, value: str) -> str:
        if not self._context.color_enabled:
            return ''

        if value in ('prev', 's', 'soft'):
            state = ColorState(insert_color_data(
                '',
                self._context.color_positions,
                self._context.color_positions_end_idx + 1
            ))
            if value == 'prev':
                prev = str(state)
                return prev if len(prev) != 0 else '\x1b[0m'
            state.set(insert_color_data(self._cur_newstring, self._cur_color_positions))
            return ColorState().get_string(compare_state=state)

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
        _, result = self._recursive_format(f'%C({value}){format_type}%Cz')
        return result

    def _do_format_truncate(self,
        value: str,
        length: int,
        location: str,
        replace: str,
        hard_length: bool
    ) -> str:
        if length < 0 or len(value) <= length:
            return value

        trunclen = length - len(replace) if hard_length else length
        truncval = ''
        if location == LEFT:
            truncval = replace + value[len(value) - trunclen:]
        elif location == MIDDLE:
            half = trunclen // 2
            truncval = value[:half] + replace + value[len(value) - (trunclen - half):]
        elif location == RIGHT:
            truncval = value[:trunclen] + replace
        return truncval

def fmt_str(string: str, color_enabled: bool = True) -> str:
    formatter = Formatter(
        context=Context(
            color_enabled=color_enabled
        )
    )
    return formatter.fmt_str(string)

def get_format_param(match: typing.Match) -> typing.Tuple[
    typing.Optional[str],
    typing.Optional[str]
]:
    formatter = _get_numbered_group(match, 'format')
    param = _get_numbered_group(match, 'param')

    if param is not None:
        param = param.replace(r'\(', '(').replace(r'\)', ')')

    return formatter, param

def _get_numbered_group(match: typing.Match, name: str, start: int = 0) -> typing.Optional[str]:
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
