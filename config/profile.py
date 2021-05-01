import re

from config import load_schema
from config.argpattern import ArgPattern
from config.fromprofile import FromProfile
from config.pattern import Pattern


class Profile:
    def __init__(self, cfg):
        self.name = None
        self.name_expression = None
        self.which = None
        self.profile_name = None

        self.arg_patterns = []
        self.from_profiles = []
        self.patterns = []

        load_schema('profile', cfg, self)

        self.name_regex = re.compile(self.name_expression) if self.name_expression else None

        if self.profile_name is not None and len(self.profile_name) == 0:
            self.profile_name = None

        for i in range(len(self.arg_patterns)):
            self.arg_patterns[i] = ArgPattern(self.arg_patterns[i])

        if not isinstance(self.from_profiles, list):
            self.from_profiles = [self.from_profiles]
        for i in range(len(self.from_profiles)):
            self.from_profiles[i] = FromProfile(self.from_profiles[i])

        for i in range(len(self.patterns)):
            self.patterns[i] = Pattern(self.patterns[i])

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
