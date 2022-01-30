import re
import typing

from ..pycolor.pyformat import fieldsep
from . import (
    BreakableStr,
    ConfigPropertyError,
    ConfigExclusivePropertyError,
    compile_re,
    join_bkstr,
    load_schema,
    mutually_exclusive,
)

ReplaceGroup = typing.Dict[typing.Union[str, int], str]

class Pattern:
    def __init__(self, cfg: dict):
        self.enabled: bool = True
        self._super_expression: BreakableStr = None
        self._expression: BreakableStr = None

        self._separator: BreakableStr = None
        self._field: typing.Union[str, int, None] = None
        self.min_fields: int = -1
        self.max_fields: int = -1

        self._replace: BreakableStr = None
        self._replace_all: BreakableStr = None
        self.replace_groups: typing.Union[ReplaceGroup, typing.List[str]] = {}
        self.replace_fields: typing.Union[ReplaceGroup, typing.List[str]] = {}
        self.filter: bool = False

        self.stdout_only: bool = False
        self.stderr_only: bool = False
        self.skip_others: bool = False

        self._activation_line: typing.Union[typing.List[int], int] = -1
        self._deactivation_line: typing.Union[typing.List[int], int] = -1

        self._activation_expression: BreakableStr = None
        self._deactivation_expression: BreakableStr = None
        self._activation_expression_line_offset: int = 0
        self._deactivation_expression_line_offset: int = 0

        self.active: bool = True
        self.regex: typing.Optional[typing.Pattern] = None
        self.super_regex: typing.Optional[typing.Pattern] = None
        self.separator_regex: typing.Optional[typing.Pattern] = None
        self.activation_regex: typing.Optional[typing.Pattern] = None
        self.deactivation_regex: typing.Optional[typing.Pattern] = None
        self._activation_exp_line_off: int = 0
        self._deactivation_exp_line_off: int = 0
        self.from_profile_str: typing.Optional[str] = None

        load_schema('pattern', cfg, self)
        mutually_exclusive(self, ['_replace', '_replace_all', 'replace_groups', 'replace_fields'])
        mutually_exclusive(self, ['stdout_only', 'stderr_only'])

        if all((
            any((
                isinstance(self._field, str),
                isinstance(self._field, int) and self._field > 0
            )),
            len(self.replace_fields) != 0
        )):
            raise ConfigExclusivePropertyError(
                '"replace_fields" cannot be used with a nonzero "field"'
            )

        self.super_expression: typing.Optional[str] = join_bkstr(self._super_expression)
        self.expression: typing.Optional[str] = join_bkstr(self._expression)
        self.separator: typing.Optional[str] = join_bkstr(self._separator)
        self.replace: typing.Optional[str] = join_bkstr(self._replace)
        self.replace_all: typing.Optional[str] = join_bkstr(self._replace_all)
        self.activation_expression: typing.Optional[str] = join_bkstr(self._activation_expression)
        self.deactivation_expression: typing.Optional[str] = join_bkstr(self._deactivation_expression)

        def as_list(var):
            return var if isinstance(var, list) else [ var ]

        self.activation_ranges: typing.List[typing.Tuple[int, bool]] = Pattern.get_activation_ranges(
            as_list(self._activation_line),
            as_list(self._deactivation_line),
        )
        if len(self.activation_ranges) != 0:
            self.active = False

        self.regex = compile_re(self.expression, 'expression')
        self.super_regex = compile_re(self.super_expression, 'super_expression')

        if self.activation_expression is not None:
            self.activation_regex = compile_re(self.activation_expression, 'activation_expression')
            self.active = False
        if self.deactivation_expression is not None:
            self.deactivation_regex = compile_re(self.deactivation_expression, 'deactivation_expression')

        if self.separator is not None and len(self.separator) != 0:
            self.separator_regex = compile_re(self.separator, 'separator')
        else:
            self.separator_regex = None
            self.field = None
            self.min_fields = -1
            self.max_fields = -1

        if self.min_fields != -1 and self.max_fields != -1 and self.min_fields > self.max_fields:
            raise ConfigPropertyError('min_fields', 'cannot be larger than max_fields')

    def get_field_indexes(self, fields_len: int) -> typing.Optional[typing.List[int]]:
        """Returns a list of field indicies that `field` matches

        Args:
            fields_len (int): Number of fields

        Returns:
            list: List of fields
        """
        fieldcount = fieldsep.idx_to_num(fields_len)
        if self.min_fields > fieldcount or (
            self.max_fields > 0 and self.max_fields < fieldcount
        ):
            return []

        if isinstance(self._field, str):
            indicies = []
            for part in self._field.split(','):
                start, stop, step = fieldsep.get_range(part, fieldcount)
                indicies.extend(list(range(
                    fieldsep.num_to_idx(start),
                    fieldsep.num_to_idx(stop) + 1,
                    step * 2
                )))
            return indicies
        if isinstance(self._field, int):
            if self._field > 0:
                if self._field > fieldcount:
                    return []
                return [fieldsep.num_to_idx(self._field)]
            return None
        return list(range(0, fields_len, 2))

    @staticmethod
    def get_activation_ranges(
        activations: typing.List[int],
        deactivations: typing.List[int]
    ) -> typing.List[typing.Tuple[int, bool]]:
        """Takes an activation and deactivation line list and converts it to a list of lines with (de)activations

        Args:
            activations (list): Activation line list
            deactivations (list): Deactivation line list

        Returns:
            list: (De)activation lines
        """
        ranges = [
            *map(lambda x: (x, True), filter(lambda x: x >= 0, activations)),
            *map(lambda x: (x, False), filter(lambda x: x >= 0, deactivations))
        ]
        ranges.sort(key=lambda x: x[0])

        if len(ranges) == 0:
            return []

        new_ranges = [ ranges[0] ]
        for line, active in ranges:
            if line != new_ranges[-1][0] and active != new_ranges[-1][1]:
                new_ranges.append((line, active))
        return new_ranges

    def is_active(self, linenum: int, data: str) -> bool:
        """Determines if pattern is active

        Args:
            linenum (int): Current line number
            data (str): Current line string

        Returns:
            bool: Returns if the pattern is active
        """
        def set_active(val: bool) -> bool:
            self.active = val
            return val

        if self._deactivation_exp_line_off > 0:
            self._deactivation_exp_line_off -= 1
            if self._deactivation_exp_line_off == 0:
                return set_active(False)
        if self._activation_exp_line_off > 0:
            self._activation_exp_line_off -= 1
            if self._activation_exp_line_off == 0:
                return set_active(True)

        if len(self.activation_ranges) != 0:
            idx, result = bsearch_closest(
                self.activation_ranges,
                linenum,
                cmp_fnc=lambda x, y: x[0] - y
            )

            if not result:
                if idx != 0:
                    idx -= 1
            if idx == 0 and self.activation_ranges[0][0] > linenum:
                is_active = not self.activation_ranges[0][1]
            else:
                is_active = self.activation_ranges[idx][1]
            if is_active != self.active:
                return set_active(is_active)

        if self.active or self._deactivation_expression_line_offset > 0:
            if self.deactivation_regex is not None and re.search(self.deactivation_regex, data):
                if self._deactivation_expression_line_offset == 0:
                    return set_active(False)
                self._deactivation_exp_line_off = self._deactivation_expression_line_offset
        if not self.active or self._activation_expression_line_offset > 0:
            if self.activation_regex is not None and re.search(self.activation_regex, data):
                if self._activation_expression_line_offset == 0:
                    return set_active(True)
                self._activation_exp_line_off = self._activation_expression_line_offset

        return self.active

def bsearch_closest(
    arr: typing.List[typing.Any],
    val: typing.Any,
    cmp_fnc: typing.Callable[[typing.Any, typing.Any], int] = lambda x, y: x - y
) -> typing.Tuple[int, bool]:
    """Binary search that returns the closest value if not found

    Args:
        arr (list): Array of values
        val (Any): Value to search for
        cmp_fnc (function): Compare function

    Returns:
        int: Index of the matching or closest matching value
    """
    low, mid, high = 0, 0, len(arr) - 1
    while low <= high:
        mid = (high + low) // 2
        if cmp_fnc(arr[mid], val) < 0:
            low = mid + 1
        elif cmp_fnc(arr[mid], val) > 0:
            high = mid - 1
        else:
            return mid, True
    return (high + low) // 2 + 1, False
