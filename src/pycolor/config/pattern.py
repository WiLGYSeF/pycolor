import re

from . import (
    ConfigPropertyError,
    compile_re,
    join_str_list,
    load_schema,
    mutually_exclusive,
)
from .. import pyformat


class Pattern:
    def __init__(self, cfg):
        self.active = True

        self.super_expression = None
        self.expression = None
        self.separator = None
        self.activation_line = None
        self.deactivation_line = None
        self.activation_expression = None
        self.deactivation_expression = None
        self.activation_expression_line_offset = 0
        self.deactivation_expression_line_offset = 0

        self.activation_exp_line_off = 0
        self.deactivation_exp_line_off = 0

        self.from_profile_str = None

        load_schema('pattern', cfg, self)

        mutually_exclusive(self, ['replace', 'replace_all'])
        mutually_exclusive(self, ['field', 'replace_groups'])
        mutually_exclusive(self, ['stdout_only', 'stderr_only'])

        for attr in [
            'expression',
            'separator',
            'replace',
            'replace_all',
            'activation_expression',
            'deactivation_expression'
        ]:
            if hasattr(self, attr):
                setattr(self, attr, join_str_list(getattr(self, attr)))

        def as_list(var):
            return var if isinstance(var, list) else [ var ]

        self.activation_ranges = Pattern.get_activation_ranges(
            as_list(self.activation_line),
            as_list(self.deactivation_line),
        )
        if len(self.activation_ranges) != 0:
            self.active = False

        self.regex = compile_re(self.expression, 'expression')
        self.super_regex = compile_re(self.super_expression, 'super_expression')

        self.activation_regex = None
        self.deactivation_regex = None

        if self.activation_expression is not None:
            self.activation_regex = compile_re(self.activation_expression, 'activation_expression')
            self.active = False
        if self.deactivation_expression is not None:
            self.deactivation_regex = compile_re(
                self.deactivation_expression,
                'deactivation_expression'
            )

        if self.separator is not None and len(self.separator) != 0:
            self.separator_regex = compile_re(self.separator, 'separator')
        else:
            self.separator_regex = None
            self.field = None
            self.min_fields = -1
            self.max_fields = -1

        if self.min_fields != -1 and self.max_fields != -1 and self.min_fields > self.max_fields:
            raise ConfigPropertyError('min_fields', 'cannot be larger than max_fields')

    def get_field_indexes(self, fields):
        """Returns a range of field indicies that field matches

        Args:
            fields (list): Fields

        Returns:
            range: The range of fields
        """
        fieldcount = pyformat.fieldsep.idx_to_num(len(fields))
        if self.min_fields > fieldcount or (
            self.max_fields > 0 and self.max_fields < fieldcount
        ):
            return range(0)

        if self.field is not None and self.field > 0:
            if self.field > fieldcount:
                return range(0)
            idx = pyformat.fieldsep.num_to_idx(self.field)
            return range(idx, idx + 1)
        return range(0, len(fields), 2)

    @staticmethod
    def get_activation_ranges(activations, deactivations):
        ranges = []
        if activations is not None and len(activations) != 0 and activations[0] is not None:
            ranges.extend(map(lambda x: (x, True), activations))
        if deactivations is not None and len(deactivations) != 0 and deactivations[0] is not None:
            ranges.extend(map(lambda x: (x, False), deactivations))

        ranges.sort(key=lambda x: x[0])

        idx = 0
        while idx < len(ranges) and ranges[idx][0] < 0:
            idx += 1
        if idx == len(ranges):
            return []

        new_ranges = [ ranges[idx] ]

        while idx < len(ranges):
            if all([
                ranges[idx][0] >= 0,
                ranges[idx][0] != new_ranges[-1][0],
                ranges[idx][1] != new_ranges[-1][1]
            ]):
                new_ranges.append(ranges[idx])
            idx += 1

        return new_ranges

    def is_active(self, linenum, data):
        def active():
            self.active = True
            return True

        def inactive():
            self.active = False
            return False

        if self.deactivation_exp_line_off > 0:
            self.deactivation_exp_line_off -= 1
            if self.deactivation_exp_line_off == 0:
                return inactive()
        if self.activation_exp_line_off > 0:
            self.activation_exp_line_off -= 1
            if self.activation_exp_line_off == 0:
                return active()

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
                active = not self.activation_ranges[0][1]
            else:
                active = self.activation_ranges[idx][1]
            if active != self.active:
                self.active = active
                return active

        if self.active or self.deactivation_expression_line_offset > 0:
            if self.deactivation_regex is not None and re.search(self.deactivation_regex, data):
                if self.deactivation_expression_line_offset == 0:
                    return inactive()
                self.deactivation_exp_line_off = self.deactivation_expression_line_offset
        if not self.active or self.activation_expression_line_offset > 0:
            if self.activation_regex is not None and re.search(self.activation_regex, data):
                if self.activation_expression_line_offset == 0:
                    return active()
                self.activation_exp_line_off = self.activation_expression_line_offset

        return self.active

def bsearch_closest(arr, val, cmp_fnc=lambda x, y: x - y):
    """Binary search that returns the closest value if not found

    Args:
        arr (list): Array of values
        val: Value to search for
        cmp_fnc (function): The compare function

    Returns:
        int: The index of the matching or closest matching value
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
