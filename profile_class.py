from pattern import Pattern
import pyformat


class Profile:
    def __init__(self, pycolor, cfg):
        self.pycolor = pycolor

        self.name = cfg.get('name')
        self.name_regex = cfg.get('name_regex')
        self.profile_name = cfg.get('profile_name')
        self.which = cfg.get('which')
        self.buffer_line = cfg.get('buffer_line', True)
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

        for pattern_cfg in cfg.get('patterns', []):
            self.patterns.append(self.init_pattern(pattern_cfg))

        for argpat in cfg.get('arg_patterns', []):
            if 'expression' not in argpat:
                continue

            self.arg_patterns.append({
                'expression': argpat['expression'],
                'position': argpat.get('position', '*'),
                'match_not': argpat.get('match_not', False),
                'optional': argpat.get('optional', False)
            })

    def init_pattern(self, cfg):
        pattern = Pattern(cfg)

        if 'replace' in cfg:
            pattern.replace = cfg['replace'].encode('utf-8')

        if 'replace_all' in cfg:
            pattern.replace_all = cfg['replace_all'].encode('utf-8')

        return pattern
