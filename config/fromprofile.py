import jsonobj


FROMPROFILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'enabled': {'type' : 'boolean', 'default': True},
        'name': {'type' : 'string', 'required': True},
        'order': {'enum': ['before', 'after'], 'default': 'before'},
    }
}


class FromProfile:
    def __init__(self, cfg):
        if isinstance(cfg, str):
            cfg = {
                'name': cfg
            }

        jsonobj.build(cfg, schema=FROMPROFILE_SCHEMA, dest=self)
