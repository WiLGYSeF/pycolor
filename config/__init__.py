import json
import os

import jsonobj


def load_schema(schema_name, cfg, dest):
    schema_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'schema')
    with open(os.path.join(schema_dir, schema_name + '.json'), 'r') as file:
        jsonobj.build(cfg, schema=json.loads(file.read()), dest=dest)
