from . import (
    ConfigPropertyError,
    compile_re,
    join_str_list,
    load_schema,
    mutually_exclusive,
)
from .argpattern import ArgPattern
from .fromprofile import FromProfile
from .pattern import Pattern


class Profile:
    def __init__(self, cfg, loader=None):
        self.name = None
        self.command = None
        self.name_expression = None
        self.command_expression = None
        self.which = None
        self.which_ignore_case = False
        self.profile_name = None

        self.arg_patterns = []
        self.min_args = None
        self.max_args = None

        self.color_aliases = {}

        self.from_profiles = []
        self.patterns = []

        self.loader = loader
        self._loaded_patterns = []
        self.patterns_loaded = False

        load_schema('profile', cfg, self)

        mutually_exclusive(self, ['name', 'command'])
        mutually_exclusive(self, ['name_expression', 'command_expression'])

        for attr in [
            'name_expression',
            'command_expression',
        ]:
            if hasattr(self, attr):
                setattr(self, attr, join_str_list(getattr(self, attr)))

        if self.name is None:
            self.name = self.command
        if self.name_expression is None:
            self.name_expression = self.command_expression

        self.name_regex = compile_re(self.name_expression, 'name_expression')

        if self.profile_name is not None and len(self.profile_name) == 0:
            self.profile_name = None

        # pylint: disable=consider-using-enumerate
        for i in range(len(self.arg_patterns)):
            self.arg_patterns[i] = ArgPattern(self.arg_patterns[i])

        if isinstance(self.min_args, int) and isinstance(self.max_args, int):
            if self.min_args > self.max_args:
                raise ConfigPropertyError('min_args', 'cannot be larger than max_args')

        if not isinstance(self.from_profiles, list):
            self.from_profiles = [self.from_profiles]
        for i in range(len(self.from_profiles)):
            self.from_profiles[i] = FromProfile(self.from_profiles[i])

    @property
    def loaded_patterns(self):
        if not self.patterns_loaded:
            self._load_patterns()
        return self._loaded_patterns

    def _load_patterns(self):
        # pylint: disable=consider-using-enumerate
        for i in range(len(self.patterns)):
            pat = Pattern(self.patterns[i])
            pat.from_profile_str = '%x' % i
            self._loaded_patterns.append(pat)

        if self.loader is not None:
            self.loader.include_from_profile(self._loaded_patterns, self.from_profiles)
        self.patterns_loaded = True

    def get_name(self):
        for name in [
            self.profile_name,
            self.which,
            self.name,
            self.name_expression,
        ]:
            if name is not None and len(name) != 0:
                return name
        return None
