import re

from config import load_schema


ARGRANGE_REGEX = re.compile(r'([<>+-])?(\*|[0-9]+)')


class ArgPattern:
    def __init__(self, cfg):
        self.expression = None
        self.position = None
        self.subcommand = []

        load_schema('argpattern', cfg, self)

        if self.expression is not None and len(self.expression) != 0:
            self.regex = re.compile(self.expression)
        else:
            self.regex = None

        if not isinstance(self.subcommand, list):
            self.subcommand = [ self.subcommand ]

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
