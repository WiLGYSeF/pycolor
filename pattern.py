import re

import jsonschema

import pyformat


PATTERN_SCHEMA = {
    'type': 'object',
    'properties': {
        'expression': {'type': 'string'},
        'enabled': {'type' : 'boolean'},

        'replace': {'type': 'string'},
        'replace_all': {'type': 'string'},
        'filter': {'type': 'boolean'},

        'start_occurrence': {'type': 'integer'},
        'max_count': {'type': 'integer'},

        'activation_line': {'type': ['array', 'integer']},
        'deactivation_line': {'type': ['array', 'integer']},
        'activation_expression': {'type': 'string'},
        'deactivation_expression': {'type': 'string'},

        'separator': {'type': 'string'},
        'field': {'type': 'integer'},
        'min_fields': {'type': 'integer'},
        'max_fields': {'type': 'integer'},

        'stdout_only': {'type' : 'boolean'},
        'stderr_only': {'type' : 'boolean'},
    },
    'required': ['expression'],
    'dependencies': {
        'field': ['separator'],
        'min_fields': ['separator'],
        'max_fields': ['separator'],
    }
}


class Pattern:
    def __init__(self, cfg):
        jsonschema.validate(instance=cfg, schema=PATTERN_SCHEMA)

        self.enabled = cfg.get('enabled', True)
        self.active = True

        self.stdout_only = cfg.get('stdout_only', False)
        self.stderr_only = cfg.get('stderr_only', False)

        self.expression = cfg['expression']
        self.filter = cfg.get('filter', False)

        self.start_occurrence = cfg.get('start_occurrence', 1)
        self.max_count = cfg.get('max_count', -1)

        activation_line = cfg.get('activation_line', -1)
        deactivation_line = cfg.get('deactivation_line', -1)

        def as_list(var):
            return var if isinstance(var, list) else [ var ]

        self.activation_ranges = Pattern.get_activation_ranges(
            as_list(activation_line),
            as_list(deactivation_line),
        )
        if len(self.activation_ranges) != 0:
            self.active = False

        self.regex = re.compile(self.expression)

        self.replace = None
        self.replace_all = None

        self.activation_expression = None
        self.activation_regex = None
        self.deactivation_expression = None
        self.deactivation_regex = None

        if cfg.get('activation_expression') is not None:
            self.activation_expression = cfg['activation_expression']
            self.activation_regex = re.compile(self.activation_expression)
            self.active = False
        if cfg.get('deactivation_expression') is not None:
            self.deactivation_expression = cfg['deactivation_expression']
            self.deactivation_regex = re.compile(self.deactivation_expression)

        self.separator = cfg.get('separator')
        self.field = cfg.get('field')
        self.min_fields = cfg.get('min_fields', -1)
        self.max_fields = cfg.get('max_fields', -1)

        if self.separator is not None and len(self.separator) == 0:
            self.separator = None
        if self.separator is None:
            self.field = None
            self.min_fields = -1
            self.max_fields = -1

        self.replace = cfg.get('replace')
        self.replace_all = cfg.get('replace_all')

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
