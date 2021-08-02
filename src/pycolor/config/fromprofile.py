from . import load_schema


class FromProfile:
    def __init__(self, cfg):
        if isinstance(cfg, str):
            cfg = {
                'name': cfg
            }

        load_schema('fromprofile', cfg, self)
