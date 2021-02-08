import re

from get_type import get_type
from pattern import Pattern


class Profile:
    def __init__(self, cfg):
        self.name = get_type(cfg, 'name', str, None)
        self.name_regex = get_type(cfg, 'name_regex', str, None)
        self.profile_name = get_type(cfg, 'profile_name', str, None)
        self.which = get_type(cfg, 'which', str, None)
        self.buffer_line = get_type(cfg, 'buffer_line', bool, True)
        self.all_args_must_match = get_type(cfg, 'all_args_must_match', bool, False)
        self.from_profiles = get_type(cfg, 'from_profiles', (list, str), [])
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

        for pattern_cfg in get_type(cfg, 'patterns', list, []):
            pattern = Pattern(pattern_cfg)

            if 'replace' in pattern_cfg:
                pattern.replace = pattern_cfg['replace']
            if 'replace_all' in pattern_cfg:
                pattern.replace_all = pattern_cfg['replace_all']

            self.patterns.append(pattern)

        for argpat in get_type(cfg, 'arg_patterns', list, []):
            if 'expression' not in argpat:
                continue

            self.arg_patterns.append({
                'expression': argpat['expression'],
                'regex': re.compile(argpat['expression']),
                'position': argpat.get('position', '*'),
                'match_not': get_type(argpat, 'match_not', bool, False),
                'optional': get_type(argpat, 'optional', bool, False)
            })
