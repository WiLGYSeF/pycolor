import json
import os

import jsonobj


DIRNAME = os.path.dirname(os.path.realpath(__file__))

schema_defs = {}


def load_schema(schema_name, cfg, dest):
    schema_dir = os.path.join(DIRNAME, 'schema')

    schema = schema_defs.get(schema_name)
    if schema is None:
        with open(os.path.join(schema_dir, schema_name + '.json'), 'r') as file:
            schema = json.loads(file.read())
        schema_defs[schema_name] = schema

    jsonobj.build(cfg, schema=schema, dest=dest)
