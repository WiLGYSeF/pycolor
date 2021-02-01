import re

from get_type import get_type


class Pattern:
    def __init__(self, cfg):
        self.enabled = get_type(cfg, 'enabled', bool, True)
        self.active = True

        self.stdout_only = get_type(cfg, 'stdout_only', bool, False)
        self.stderr_only = get_type(cfg, 'stderr_only', bool, False)

        self.expression = cfg['expression']
        self.filter = get_type(cfg, 'filter', bool, False)

        self.start_occurrance = get_type(cfg, 'start_occurrance', int, 1)
        self.max_count = get_type(cfg, 'max_count', int, -1)

        self.activation_line = get_type(cfg, 'activation_line', int, -1)
        self.deactivation_line = get_type(cfg, 'deactivation_line', int, -1)

        self.regex = re.compile(cfg['expression'].encode('utf-8'))

        self.replace = None
        self.replace_all = None

        self.activation_expression = None
        self.activation_regex = None
        self.deactivation_expression = None
        self.deactivation_regex = None

        if cfg.get('activation_expression') is not None:
            self.activation_expression = cfg['activation_expression']
            self.activation_regex = re.compile(
                cfg['activation_expression'].encode('utf-8')
            )
            self.active = False
        if cfg.get('deactivation_expression') is not None:
            self.deactivation_expression = cfg['deactivation_expression']
            self.deactivation_regex = re.compile(
                cfg['deactivation_expression'].encode('utf-8')
            )

        self.separator = get_type(cfg, 'separator', str, None)
        self.field = get_type(cfg, 'field', int, None)
        self.min_fields = get_type(cfg, 'min_fields', int, -1)
        self.max_fields = get_type(cfg, 'max_fields', int, -1)

        if self.separator is not None and len(self.separator) == 0:
            self.separator = None
        if self.separator is not None:
            self.separator = self.separator.encode('utf-8')
        else:
            self.field = None
            self.min_fields = -1
            self.max_fields = -1

    def is_line_active(self, linenum):
        if self.activation_line > -1 and self.activation_line > linenum:
            return False
        if self.deactivation_line > -1 and self.deactivation_line <= linenum:
            return False
        return True
