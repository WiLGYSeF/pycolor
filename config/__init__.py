import json
import os

import fastjsonschema


DIRNAME = os.path.dirname(os.path.realpath(__file__))

validators = {}

def load_schema(schema_name, cfg, dest):
    schema_dir = os.path.join(DIRNAME, 'schema')

    validator = validators.get(schema_name)
    if validator is None:
        with open(os.path.join(schema_dir, schema_name + '.json'), 'r') as file:
            validator = fastjsonschema.compile(json.loads(file.read()))
        validators[schema_name] = validator

    validator(cfg)
    for key, val in cfg.items():
        setattr(dest, key, val)

def join_str_list(val):
    return ''.join(val) if isinstance(val, list) else val
