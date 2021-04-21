import re

import jsonschema


ARGPATTERN_SCHEMA = {
    'type': 'object',
    'properties': {
        'expression': {'type': ['array', 'string']},
        'position': {'type': ['string', 'integer', 'null']},

        'match_not': {'type': 'boolean'},
        'optional': {'type': 'boolean'},
    },
    'required': ['expression']
}

ARGRANGE_REGEX = re.compile(r'([<>+-])?(\*|[0-9]+)')


class ArgPattern:
    def __init__(self, cfg):
        jsonschema.validate(instance=cfg, schema=ARGPATTERN_SCHEMA)

        self.expression = cfg['expression']
        if isinstance(self.expression, list):
            self.expression = ''.join(self.expression)
        self.regex = re.compile(self.expression)

        self.position = cfg.get('position', '*')
        self.match_not = cfg.get('match_not', False)
        self.optional = cfg.get('optional', False)

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
