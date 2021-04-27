import re

import jsonobj


ARGPATTERN_SCHEMA = {
    'type': 'object',
    'properties': {
        'expression': {'type': ['string_array']},
        'position': {'type': ['null', 'string', 'integer']},

        'match_not': {'type': 'boolean'},
        'optional': {'type': 'boolean'},
    },
    'required': ['expression']
}

ARGRANGE_REGEX = re.compile(r'([<>+-])?(\*|[0-9]+)')


class ArgPattern:
    def __init__(self, cfg):
        self.expression = None
        self.position = None

        jsonobj.build(cfg, schema=ARGPATTERN_SCHEMA, dest=self)

        self.regex = re.compile(self.expression)

    def get_arg_range(self, arglen):
        if self.position is None:
            return range(arglen)

        if isinstance(self.position, int):
            if self.position > arglen:
                return range(0)
            return range(self.position - 1, self.position)

        match = ARGRANGE_REGEX.fullmatch(self.position)
        if match is None:
            return range(arglen)

        index = match[2]
        if index == '*':
            return range(arglen)
        index = int(index)

        arg_range = None
        modifier = match[1]

        if modifier is None:
            arg_range = range(index - 1, min(index, arglen))
        elif modifier in ('>', '+'):
            arg_range = range(index - 1, arglen)
        elif modifier in ('<', '-'):
            arg_range = range(0, min(index, arglen))
        return arg_range
