import re

from config import load_schema, compile_re, mutually_exclusive, join_str_list


ARGRANGE_REGEX = re.compile(r'([<>+-])?(\*|[0-9]+)')


class ArgPattern:
    def __init__(self, cfg):
        self.expression = None
        self.position = None
        self.subcommand = []

        load_schema('argpattern', cfg, self)

        mutually_exclusive(self, ['expression', 'subcommand'])

        for attr in [
            'expression',
        ]:
            if hasattr(self, attr):
                setattr(self, attr, join_str_list(getattr(self, attr)))

        self.regex = compile_re(self.expression, 'expression')

        if not isinstance(self.subcommand, list):
            self.subcommand = [ self.subcommand ]

    def get_arg_range(self, arglen):
        """Returns a range of argument indicies that position matches

        Args:
            arglen (int): The length of the arguments

        Returns:
            range: Range of matching indicies
        """
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
