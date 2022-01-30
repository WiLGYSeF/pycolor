import json
import os
import re
import typing

import fastjsonschema

DIRNAME = os.path.dirname(os.path.realpath(__file__))
SAMPLE_CONFIG_DIR = os.path.join(DIRNAME, 'sample-config')
SCHEMA_DIR = os.path.join(DIRNAME, 'schema')

BreakableStr = typing.Union[typing.List[str], str, None]

_validators: typing.Dict[str, typing.Callable[[dict], None]] = {}

class ConfigError(Exception):
    def __init__(self, message: str):
        self.message: str = message
        super().__init__(self.message)

class ConfigPropertyError(ConfigError):
    def __init__(self, prop: str, message: str):
        self.property: str = prop
        super().__init__('"%s": %s' % (self.property, message))

class ConfigRegexError(ConfigPropertyError):
    def __init__(self, prop: str, message: str):
        super().__init__(prop, 'regex %s' % message)

class ConfigExclusivePropertyError(ConfigError):
    pass

def load_schema(schema_name: str, cfg: dict, dest: typing.Any) -> None:
    """Validates and loads object to destination

    Args:
        schema_name (str): Name of schema
        cfg (dict): Object to validate and load
        dest (Any): Object being loaded to
    """
    validator = _validators.get(schema_name)
    if validator is None:
        with open(os.path.join(SCHEMA_DIR, schema_name + '.json'), 'r') as file:
            validator = fastjsonschema.compile(json.loads(file.read()))
        _validators[schema_name] = validator

    try:
        validator(cfg)
    except fastjsonschema.JsonSchemaException as jse:
        raise ConfigError(jse) from jse

    for key, val in cfg.items():
        if hasattr(dest, '_' + key):
            setattr(dest, '_' + key, val)
        elif hasattr(dest, key):
            setattr(dest, key, val)

def compile_re(expression: typing.Optional[str], prop: str) -> typing.Optional[typing.Pattern]:
    if expression is None:
        return None
    try:
        return re.compile(expression) if len(expression) != 0 else None
    except re.error as rer:
        raise ConfigRegexError(prop, str(rer)) from rer

def mutually_exclusive(obj: typing.Any, attrlist: typing.Iterable[str]) -> None:
    """Checks that at most one attribute is set from the list

    Throws if the attributes are not mutually exclusive

    Args:
        obj (Any): Object with attributes
        arrlist (list): List of attribute names that should be mutually exclusive
    """
    count = 0
    for attr in attrlist:
        if not hasattr(obj, attr):
            raise AttributeError('%s is missing attribute: %s' % (type(obj), attr))
        val = getattr(obj, attr)
        if any((
            isinstance(val, bool) and val is False,
            isinstance(val, (dict, list)) and len(val) == 0,
            isinstance(val, int) and val == -1, # TODO: replace with something more concrete
            val is None,
        )):
            continue
        count += 1
    if count > 1:
        raise ConfigExclusivePropertyError('mutually exclusive: %s' % str(list(map(
            lambda x: x[1:] if x[0] == '_' else x,
            attrlist
        ))))

def join_bkstr(val: BreakableStr) -> typing.Optional[str]:
    """Joins a BreakableStr to a str

    Args:
        val (BreakableStr): (Un)broken string

    Returns:
        str: The joined string
    """
    if val is None:
        return None
    return ''.join(val) if isinstance(val, list) else val
