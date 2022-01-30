import typing

from . import (
    BreakableStr,
    ConfigPropertyError,
    compile_re,
    join_bkstr,
    load_schema,
    mutually_exclusive,
)
from .argpattern import ArgPattern
from .fromprofile import FromProfile
from .pattern import Pattern

class Profile:
    def __init__(self, cfg: dict, loader = None):
        self.enabled: bool = True
        self.name: typing.Optional[str] = None
        self.command: typing.Optional[str] = None
        self._name_expression: BreakableStr = None
        self._command_expression: BreakableStr = None
        self.profile_name: typing.Optional[str] = None
        self.which: typing.Optional[str] = None
        self.which_ignore_case: bool = False

        self._arg_patterns: typing.List[dict] = []
        self.min_args: typing.Optional[int] = None
        self.max_args: typing.Optional[int] = None

        self.timestamp: typing.Union[str, bool] = False
        self.tty: bool = False
        self.nobuffer: bool = False
        self.remove_input_color: bool = False

        self.color_aliases: typing.Dict[str, str] = {}

        self._from_profiles: typing.Union[typing.List[dict], dict, str] = []
        self.patterns: typing.List[dict] = []

        self._loader = loader
        self._loaded_patterns: typing.List[Pattern] = []
        self._patterns_loaded: bool = False

        self.from_profile_str: typing.Optional[str] = None

        load_schema('profile', cfg, self)
        mutually_exclusive(self, ['name', 'command'])
        mutually_exclusive(self, ['_name_expression', '_command_expression'])

        self.name_expression: typing.Optional[str] = join_bkstr(self._name_expression)
        self.command_expression: typing.Optional[str] = join_bkstr(self._command_expression)

        if self.name is None:
            self.name = self.command
        if self.name_expression is None:
            self.name_expression = self.command_expression

        self.name_regex = compile_re(self.name_expression, 'name_expression')

        if self.profile_name is not None and len(self.profile_name) == 0:
            self.profile_name = None

        self.arg_patterns: typing.List[ArgPattern] = [
            ArgPattern(pat) for pat in self._arg_patterns
        ]

        if isinstance(self.min_args, int) and isinstance(self.max_args, int):
            if self.min_args > self.max_args:
                raise ConfigPropertyError('min_args', 'cannot be larger than max_args')

        self.from_profiles: typing.List[FromProfile] = [
            FromProfile(prof) for prof in (
                self._from_profiles if isinstance(self._from_profiles, list) else [self._from_profiles] # type: ignore
            )
        ]

    @property
    def loaded_patterns(self) -> typing.List[Pattern]:
        if not self._patterns_loaded:
            self.load_patterns()
        return self._loaded_patterns

    def load_patterns(self) -> None:
        """Load patterns
        """
        idx = 0
        for pattern in self.patterns:
            pat = Pattern(pattern)
            pat.from_profile_str = '%x' % idx
            self._loaded_patterns.append(pat)
            idx += 1

        if self._loader is not None:
            self._loader.include_from_profile(self._loaded_patterns, self.from_profiles)
        self._patterns_loaded = True

    def get_name(self) -> typing.Optional[str]:
        """Gets the profile name

        Returns:
            str: Profile name
        """
        for name in [
            self.profile_name,
            self.which,
            self.name,
            self.name_expression,
        ]:
            if name is not None and len(name) != 0:
                return name
        return None
