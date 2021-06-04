import json
import os
import re

import fastjsonschema


DIRNAME = os.path.dirname(os.path.realpath(__file__))
SCHEMA_DIR = os.path.join(DIRNAME, 'schema')

validators = {}


class ConfigException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ConfigPropertyException(ConfigException):
    def __init__(self, prop, message):
        self.property = prop
        super().__init__('"%s": %s' % (self.property, message))

class ConfigRegexException(ConfigPropertyException):
    def __init__(self, prop, message):
        super().__init__(prop, 'regex %s' % message)

def load_schema(schema_name, cfg, dest):
    validator = validators.get(schema_name)
    if validator is None:
        with open(os.path.join(SCHEMA_DIR, schema_name + '.json'), 'r') as file:
            validator = fastjsonschema.compile(json.loads(file.read()))
        validators[schema_name] = validator

    try:
        validator(cfg)
    except fastjsonschema.JsonSchemaException as jse:
        raise ConfigException(jse) from jse

    for key, val in cfg.items():
        setattr(dest, key, val)

def compile_re(expression, prop):
    if expression is None:
        return None
    try:
        return re.compile(expression) if len(expression) != 0 else None
    except re.error as rer:
        raise ConfigRegexException(prop, rer) from rer

def join_str_list(val):
    if val is None:
        return None
    return ''.join(val) if isinstance(val, list) else val
