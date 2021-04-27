import re

import jsonobj
import pyformat


PATTERN_SCHEMA = {
    'type': 'object',
    'properties': {
        'enabled': {'type' : 'boolean', 'default': True},
        'super_expression': {'type': ['null', 'string_array']},
        'expression': {'type': ['string_array'], 'required': True},

        'separator': {'type': ['null', 'string_array']},
        'field': {'type': ['null', 'integer'], 'default': None},
        'min_fields': {'type': 'integer', 'default': -1},
        'max_fields': {'type': 'integer', 'default': -1},

        'replace': {'type': ['null', 'string_array']},
        'replace_all': {'type': ['null', 'string_array']},
        'replace_groups': {'type': ['array', 'object'], 'default': {}},
        'replace_fields': {'type': ['array', 'object'], 'default': {}},
        'filter': {'type': 'boolean'},

        'stdout_only': {'type' : 'boolean'},
        'stderr_only': {'type' : 'boolean'},
        'skip_others': {'type': 'boolean'},

        'start_occurrence': {'type': 'integer', 'default': 1},
        'max_count': {'type': 'integer', 'default': -1},

        'activation_line': {'type': ['array', 'integer'], 'default': -1},
        'deactivation_line': {'type': ['array', 'integer'], 'default': -1},

        'activation_expression': {'type': ['null', 'string_array']},
        'deactivation_expression': {'type': ['null', 'string_array']},
    },
    'dependencies': {
        'field': ['separator'],
        'min_fields': ['separator'],
        'max_fields': ['separator'],
    }
}


class Pattern:
    def __init__(self, cfg):
        self.active = True

        self.activation_line = None
        self.deactivation_line = None
        self.expression = None
        self.super_expression = None
        self.activation_expression = None
        self.deactivation_expression = None
        self.separator = None

        jsonobj.build(cfg, schema=PATTERN_SCHEMA, dest=self)

        def as_list(var):
            return var if isinstance(var, list) else [ var ]

        self.activation_ranges = Pattern.get_activation_ranges(
            as_list(self.activation_line),
            as_list(self.deactivation_line),
        )
        if len(self.activation_ranges) != 0:
            self.active = False

        self.regex = re.compile(self.expression)
        self.super_regex = re.compile(self.super_expression) if self.super_expression else None

        self.activation_regex = None
        self.deactivation_regex = None

        if self.activation_expression is not None:
            self.activation_regex = re.compile(self.activation_expression)
            self.active = False
        if self.deactivation_expression is not None:
            self.deactivation_regex = re.compile(self.deactivation_expression)

        if self.separator is not None and len(self.separator) != 0:
            self.separator_regex = re.compile(self.separator)
        else:
            self.separator_regex = None
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
