import re


class Pattern:
    def __init__(self, cfg):
        self.enabled = cfg.get('enabled', True)
        self.active = True

        self.stdout_only = cfg.get('stdout_only', False)
        self.stderr_only = cfg.get('stderr_only', False)

        self.expression = cfg['expression']
        self.filter = cfg.get('filter', False)

        self.start_occurrance = cfg.get('start_occurrance', 1)
        self.max_count = cfg.get('max_count', -1)

        self.activation_line = cfg.get('activation_line', -1)
        self.deactivation_line = cfg.get('deactivation_line', -1)

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

        self.separator = cfg.get('separator')
        self.field = cfg.get('field')
        self.min_fields = cfg.get('min_fields', -1)
        self.max_fields = cfg.get('max_fields', -1)

        if self.separator is not None and len(self.separator) == 0:
            self.separator = None
        if self.separator is None:
            self.field = None
            self.min_fields = -1
            self.max_fields = -1

    def is_line_active(self, linenum):
        if self.activation_line > -1 and self.activation_line > linenum:
            return False
        if self.deactivation_line > -1 and self.deactivation_line <= linenum:
            return False
        return True
