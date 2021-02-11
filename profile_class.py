import jsonschema

import argpattern
import pattern


PROFILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type' : 'string'},
        'name_regex': {'type' : 'string'},
        'profile_name': {'type': 'string'},
        'which': {'type': 'string'},
        'buffer_line': {'type': 'boolean'},
        'all_args_must_match': {'type': 'boolean'},
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
        self.from_profiles = cfg.get('from_profiles', [])
        self.patterns = []
        self.arg_patterns = []

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

        for pat in cfg.get('patterns', []):
            self.patterns.append(pattern.Pattern(pat))
