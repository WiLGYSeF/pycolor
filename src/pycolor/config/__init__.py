import json
import os
import re

import fastjsonschema


DIRNAME = os.path.dirname(os.path.realpath(__file__))
SCHEMA_DIR = os.path.join(DIRNAME, 'schema')

validators = {}


class ConfigError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ConfigPropertyError(ConfigError):
    def __init__(self, prop, message):
        self.property = prop
        super().__init__('"%s": %s' % (self.property, message))

class ConfigRegexError(ConfigPropertyError):
    def __init__(self, prop, message):
        super().__init__(prop, 'regex %s' % message)

class ConfigExclusivePropertyError(ConfigError):
    pass

def load_schema(schema_name, cfg, dest):
    validator = validators.get(schema_name)
    if validator is None:
        with open(os.path.join(SCHEMA_DIR, schema_name + '.json'), 'r') as file:
            validator = fastjsonschema.compile(json.loads(file.read()))
        validators[schema_name] = validator

    try:
        validator(cfg)
    except fastjsonschema.JsonSchemaException as jse:
        raise ConfigError(jse) from jse

    for key, val in cfg.items():
        setattr(dest, key, val)

def compile_re(expression, prop):
    if expression is None:
        return None
    try:
        return re.compile(expression) if len(expression) != 0 else None
    except re.error as rer:
        raise ConfigRegexError(prop, rer) from rer

def mutually_exclusive(self, attrlist):
    count = 0
    for attr in attrlist:
        if not hasattr(self, attr):
            continue
        val = getattr(self, attr)
        if any([
            isinstance(val, bool) and val is False,
            isinstance(val, (dict, list)) and len(val) == 0,
            isinstance(val, int) and val == -1, # TODO: replace with something more concrete
            val is None,
        ]):
            continue
        count += 1
    if count > 1:
        raise ConfigExclusivePropertyError('mutually exclusive: %s' % str(attrlist))

def join_str_list(val):
    if val is None:
        return None
    return ''.join(val) if isinstance(val, list) else val
