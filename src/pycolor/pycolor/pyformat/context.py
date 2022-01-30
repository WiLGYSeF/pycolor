import typing

from .coloring import ColorPositions

class Context:
    def __init__(self, **kwargs):
        self.color_enabled: bool = kwargs.get('color_enabled', True)
        self.color_aliases: typing.Dict[str, str] = kwargs.get('color_aliases', {})
        self.color_positions: ColorPositions = kwargs.get('color_positions', {})
        self.color_positions_end_idx: int = kwargs.get('color_positions_end_idx', -1)

        self.fields: typing.List[str] = kwargs.get('fields', [])
        self.field_cur: typing.Optional[str] = kwargs.get('field_cur')

        self.match: typing.Optional[typing.Match] = kwargs.get('match')
        self.match_cur: typing.Optional[str] = kwargs.get('match_cur')
        self.match_incr: typing.Optional[int] = kwargs.get('match_incr')

    def copy_color_positions(self):
        colorpos = {}
        for key, val in self.color_positions.items():
            colorpos[key] = val
        return colorpos

    def copy(self) -> 'Context':
        """Copies the context

        Returns:
            Context: copied context
        """
        ctx = Context()

        ctx.color_enabled = self.color_enabled
        ctx.color_positions = self.color_positions
        ctx.color_aliases = self.color_aliases

        ctx.fields = self.fields
        ctx.field_cur = self.field_cur

        ctx.match = self.match
        ctx.match_cur = self.match_cur
        ctx.match_incr = self.match_incr

        return ctx
