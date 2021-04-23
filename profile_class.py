import re

import jsonobj

import argpattern
import fromprofile
import pattern


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

        jsonobj.build(cfg, schema=PROFILE_SCHEMA, dest=self)

        self.from_profiles = []

        self.arg_patterns = []
        self.patterns = []

        self.name_regex = re.compile(self.name_expression) if self.name_expression else None

        if self.profile_name is not None and len(self.profile_name) == 0:
            self.profile_name = None

        """
        if not any([
            self.name,
            self.name_expression,
            self.profile_name
        ]):
            raise ValueError()
        """

        for argpat in cfg.get('arg_patterns', []):
            self.arg_patterns.append(argpattern.ArgPattern(argpat))

        if 'from_profiles' in cfg:
            from_profiles = cfg['from_profiles']
            if isinstance(from_profiles, list):
                for fromprof in from_profiles:
                    self.from_profiles.append(fromprofile.FromProfile(fromprof))
            else:
                self.from_profiles.append(fromprofile.FromProfile(from_profiles))

        for pat in cfg.get('patterns', []):
            self.patterns.append(pattern.Pattern(pat))

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
