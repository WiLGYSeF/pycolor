from pattern import Pattern
import pyformat


class Profile:
    def __init__(self, pycolor, cfg):
        self.name = cfg.get('name')
        self.name_regex = cfg.get('name_regex')
        self.profile_name = cfg.get('profile_name')
        self.which = cfg.get('which')
        self.arg_patterns = cfg.get('arg_patterns', [])
        self.buffer_line = cfg.get('buffer_line', True)
        self.from_profiles = cfg.get('from_profiles', [])
        self.patterns = []

        if not any([
            self.name,
            self.name_regex,
            self.profile_name
        ]):
            raise ValueError()

        for pattern_cfg in cfg.get('patterns', []):
            self.patterns.append(init_pattern(pycolor, pattern_cfg))


def init_pattern(pycolor, cfg):
    pattern = Pattern(cfg)

    if 'replace' in cfg:
        pattern.replace = pyformat.format_string(
            cfg['replace'],
            context={
                'color_enabled': pycolor.is_color_enabled()
            }
        ).encode('utf-8')

    if 'replace_all' in cfg:
        pattern.replace_all = pyformat.format_string(
            cfg['replace_all'],
            context={
                'color_enabled': pycolor.is_color_enabled()
            }
        ).encode('utf-8')

    return pattern
