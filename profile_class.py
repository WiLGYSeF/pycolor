import re

import jsonschema

import argpattern
import fromprofile
import pattern


PROFILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type' : 'string'},
        'name_expression': {'type' : ['array', 'string']},
        'profile_name': {'type': 'string'},
        'which': {'type': 'string'},

        'all_args_must_match': {'type': 'boolean'},
        'min_args': {'type': 'integer'},
        'max_args': {'type': 'integer'},
        'soft_reset_eol': {'type': 'boolean'},
        'timestamp': {'type': ['boolean', 'string']},
        'less_output': {'type': 'boolean'},
        'tty': {'type': 'boolean'},

        'from_profiles': {'type': ['array', 'string']},

        'arg_patterns': {'type': 'array'},
        'patterns': {'type': 'array'},
    },
    'required': []
}


class Profile:
    def __init__(self, cfg):
        jsonschema.validate(instance=cfg, schema=PROFILE_SCHEMA)

        self.name = cfg.get('name')
        self.name_expression = cfg.get('name_expression')
        self.profile_name = cfg.get('profile_name')
        self.which = cfg.get('which')

        self.all_args_must_match = cfg.get('all_args_must_match', False)
        self.min_args = cfg.get('min_args')
        self.max_args = cfg.get('max_args')
        self.soft_reset_eol = cfg.get('soft_reset_eol', False)
        self.timestamp = cfg.get('timestamp', False)
        self.less_output = cfg.get('less_output', False)
        self.tty = cfg.get('tty', False)

        self.from_profiles = []

        self.arg_patterns = []
        self.patterns = []

        if isinstance(self.name_expression, list):
            self.name_expression = ''.join(self.name_expression)

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
