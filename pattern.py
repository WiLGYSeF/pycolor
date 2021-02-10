import re

from get_type import get_type
import pyformat


class Pattern:
    def __init__(self, cfg):
        self.enabled = get_type(cfg, 'enabled', bool, True)
        self.active = True

        self.stdout_only = get_type(cfg, 'stdout_only', bool, False)
        self.stderr_only = get_type(cfg, 'stderr_only', bool, False)

        self.expression = cfg['expression']
        self.filter = get_type(cfg, 'filter', bool, False)

        self.start_occurrence = get_type(cfg, 'start_occurrence', int, 1)
        self.max_count = get_type(cfg, 'max_count', int, -1)

        if 'activation_lines' in cfg:
            activation_line = get_type(cfg, 'activation_lines', list, [])
        else:
            activation_line = get_type(cfg, 'activation_line', (list, int), -1)
        if 'deactivation_lines' in cfg:
            deactivation_line = get_type(cfg, 'deactivation_lines', list, [])
        else:
            deactivation_line = get_type(cfg, 'deactivation_line', (list, int), -1)

        def as_list(var):
            return var if isinstance(var, list) else [ var ]

        self.activation_ranges = Pattern.get_activation_ranges(
            as_list(activation_line),
            as_list(deactivation_line),
        )
        if len(self.activation_ranges) != 0:
            self.active = False

        self.regex = re.compile(cfg['expression'])

        self.replace = None
        self.replace_all = None

        self.activation_expression = None
        self.activation_regex = None
        self.deactivation_expression = None
        self.deactivation_regex = None

        if cfg.get('activation_expression') is not None:
            self.activation_expression = cfg['activation_expression']
            self.activation_regex = re.compile(cfg['activation_expression'])
            self.active = False
        if cfg.get('deactivation_expression') is not None:
            self.deactivation_expression = cfg['deactivation_expression']
            self.deactivation_regex = re.compile(cfg['deactivation_expression'])

        self.separator = get_type(cfg, 'separator', str, None)
        self.field = get_type(cfg, 'field', int, None)
        self.min_fields = get_type(cfg, 'min_fields', int, -1)
        self.max_fields = get_type(cfg, 'max_fields', int, -1)

        if self.separator is not None and len(self.separator) == 0:
            self.separator = None
        if self.separator is None:
            self.field = None
            self.min_fields = -1
            self.max_fields = -1

    def get_field_indexes(self, fields):
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
        ranges.extend(map(lambda x: (x, True), activations))
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
                return inactive() if self.activation_ranges[0][1] else active()
            return active() if self.activation_ranges[idx][1] else inactive()

        if self.active:
            if self.deactivation_regex is not None and re.search(self.deactivation_regex, data):
                return inactive()
        else:
            if self.activation_regex is not None and re.search(self.activation_regex, data):
                return active()

        return self.active

def bsearch_closest(arr, val, cmp_fnc=lambda x, y: x - y):
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
