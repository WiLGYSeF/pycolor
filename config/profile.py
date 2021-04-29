import re

import jsonobj

from config.argpattern import ArgPattern
from config.fromprofile import FromProfile
from config.pattern import Pattern


PROFILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type' : ['null', 'string']},
        'name_expression': {'type' : ['null', 'string_array']},
        'profile_name': {'type': ['null', 'string']},
        'which': {'type': ['null', 'string']},

        'all_args_must_match': {'type': 'boolean'},
        'min_args': {'type': ['null', 'integer']},
        'max_args': {'type': ['null', 'integer']},

        'soft_reset_eol': {'type': 'boolean'},
        'timestamp': {'type': ['boolean', 'string']},
        'less_output': {'type': ['boolean', 'string']},
        'tty': {'type': 'boolean'},

        'from_profiles': {'type': ['array', 'object', 'string']},

        'arg_patterns': {'type': 'array'},
        'patterns': {'type': 'array'},
    }
}


class Profile:
    def __init__(self, cfg):
        self.name = None
        self.name_expression = None
        self.which = None
        self.profile_name = None

        self.arg_patterns = []
        self.from_profiles = []
        self.patterns = []

        jsonobj.build(cfg, schema=PROFILE_SCHEMA, dest=self)

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
