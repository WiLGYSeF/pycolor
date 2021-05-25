import json
import os

import fastjsonschema


def load_schema(schema_name, cfg, dest):
    schema_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'schema')
    with open(os.path.join(schema_dir, schema_name + '.json'), 'r') as file:
        fastjsonschema.validate(json.loads(file.read()), cfg)
        for key, val in cfg.items():
            setattr(dest, key, val)

def join_str_list(val):
    return ''.join(val) if isinstance(val, list) else val
