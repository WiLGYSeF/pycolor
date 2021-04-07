import jsonschema

import argpattern
import fromprofile
import pattern


PROFILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type' : 'string'},
        'name_regex': {'type' : ['array', 'string']},
        'profile_name': {'type': 'string'},
        'which': {'type': 'string'},

        'buffer_line': {'type': 'boolean'},
        'all_args_must_match': {'type': 'boolean'},
        'soft_reset_eol': {'type': 'boolean'},
        'timestamp': {'type': ['boolean', 'string']},

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
        self.name_regex = cfg.get('name_regex')
        self.profile_name = cfg.get('profile_name')
        self.which = cfg.get('which')

        self.buffer_line = cfg.get('buffer_line', True)
        self.all_args_must_match = cfg.get('all_args_must_match', False)
        self.soft_reset_eol = cfg.get('soft_reset_eol', False)
        self.timestamp = cfg.get('timestamp', False)

        self.from_profiles = []

        self.arg_patterns = []
        self.patterns = []

        if isinstance(self.name_regex, list):
            self.name_regex = ''.join(self.name_regex)

        if self.profile_name is not None and len(self.profile_name) == 0:
            self.profile_name = None

        if not any([
            self.name,
            self.name_regex,
            self.profile_name
        ]):
            raise ValueError()

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
