import re
import typing

from . import (
    BreakableStr,
    ConfigPropertyError,
    compile_re,
    join_bkstr,
    load_schema,
    mutually_exclusive,
)

ARGRANGE_REGEX = re.compile(r'([<>+-])?(\*|[0-9]+)')

class ArgPattern:
    def __init__(self, cfg: dict):
        self.enabled: bool = True
        self._expression: BreakableStr = None
        self._subcommand: typing.Union[typing.List[str], str] = []
        self.position: typing.Union[int, str, None] = None

        self.match_not: bool = False
        self.optional: bool = False

        load_schema('argpattern', cfg, self)
        mutually_exclusive(self, ['_expression', '_subcommand'])

        self.expression: typing.Optional[str] = join_bkstr(self._expression)
        self.regex: typing.Optional[typing.Pattern] = compile_re(self.expression, 'expression')

        self.subcommand: typing.List[str] = []
        if isinstance(self._subcommand, str):
            self.subcommand = [ self._subcommand ]
        else:
            self.subcommand = self._subcommand

        if isinstance(self.position, str) and not ARGRANGE_REGEX.match(self.position):
            raise ConfigPropertyError('position', 'is not a valid argument position')

    def get_arg_range(self, arglen: int) -> range:
        """Returns a range of argument indicies that position matches

        Args:
            arglen (int): Length of the arguments

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

        idx = int(index)
        modifier = match[1]
        arg_range = range(0)

        if modifier is None:
            arg_range = range(idx - 1, min(idx, arglen))
        elif modifier in ('>', '+'):
            arg_range = range(idx - 1, arglen)
        elif modifier in ('<', '-'):
            arg_range = range(0, min(idx, arglen))
        return arg_range
