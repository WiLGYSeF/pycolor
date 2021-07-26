from config import (
    ConfigPropertyError,
    compile_re,
    join_str_list,
    load_schema,
    mutually_exclusive,
)
from config.argpattern import ArgPattern
from config.fromprofile import FromProfile
from config.pattern import Pattern


class Profile:
    def __init__(self, cfg):
        self.name = None
        self.command = None
        self.name_expression = None
        self.command_expression = None
        self.which = None
        self.profile_name = None

        self.arg_patterns = []
        self.min_args = None
        self.max_args = None
        self.from_profiles = []
        self.patterns = []

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

        for i in range(len(self.arg_patterns)):
            self.arg_patterns[i] = ArgPattern(self.arg_patterns[i])

        if isinstance(self.min_args, int) and isinstance(self.max_args, int):
            if self.min_args > self.max_args:
                raise ConfigPropertyError('min_args', 'cannot be larger than max_args')

        if not isinstance(self.from_profiles, list):
            self.from_profiles = [self.from_profiles]
        for i in range(len(self.from_profiles)):
            self.from_profiles[i] = FromProfile(self.from_profiles[i])

        for i in range(len(self.patterns)):
            self.patterns[i] = Pattern(self.patterns[i])
            self.patterns[i].from_profile_str = '%x' % i

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
