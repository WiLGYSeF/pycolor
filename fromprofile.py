import jsonschema


FROMPROFILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'enabled': {'type' : 'boolean'},
        'name': {'type' : 'string'},
        'order': {'enum': ['before', 'after']},
    },
    'required': ['name']
}


class FromProfile:
    def __init__(self, cfg):
        if isinstance(cfg, str):
            cfg = {
                'name': cfg
            }

        jsonschema.validate(instance=cfg, schema=FROMPROFILE_SCHEMA)

        self.enabled = cfg.get('enabled', True)
        self.name = cfg['name']
        self.order = cfg.get('order', 'after')
