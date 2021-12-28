from . import load_schema

class FromProfile:
    def __init__(self, cfg: dict):
        if isinstance(cfg, str):
            cfg = {
                'name': cfg
            }

        self.enabled: bool = False
        self.name: str = ''
        self.order: str = 'before'

        load_schema('fromprofile', cfg, self)
