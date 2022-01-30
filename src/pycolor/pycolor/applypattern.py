import typing

from ..config.pattern import Pattern, ReplaceGroup
from ..strman.match_group_replace import match_group_replace
from ..strman.search_replace import search_replace, ReplaceRange
from ..strman.split import re_split
from ..utils.group_index import get_named_group_at_index
from . import pyformat
from .pyformat import Formatter
from .pyformat.coloring.colorpositions import (
    update_color_positions,
    update_color_positions_replace_ranges,
    offset_color_positions
)
from .pyformat.context import Context, ColorPositions

def apply_pattern(
    pat: Pattern,
    data: str,
    context: Context
) -> typing.Tuple[bool, typing.Optional[str]]:
    """Applies the pattern to the input

    Args:
        pat (Pattern): Pattern to apply
        data (str): Input data
        context (Context): Context

    Returns:
        tuple: Returns true if a match was found, and the new string
    """
    if pat.super_regex is not None and not pat.super_regex.search(data):
        return False, None

    fields: typing.List[str] = []
    field_idxs: typing.Optional[typing.List[int]] = []

    if pat.separator_regex is not None:
        fields = list(re_split(pat.separator_regex, data))
        field_idxs = pat.get_field_indexes(len(fields))
        context.fields = fields
    else:
        fields = [data]
        field_idxs = [0]

    changed = False
    result = None

    if len(pat.replace_fields) == 0:
        if field_idxs is None:
            fields = [data]
            field_idxs = [0]

        if pat.regex is not None:
            if pat.replace_all is not None:
                def replace_func(data: str, index: int, offset: int):
                    match = pat.regex.search(data) # type: ignore
                    if match is None:
                        return data, [], {}

                    context.match = match
                    result, colorpos = Formatter(context=context).format_string(pat.replace_all) # type: ignore
                    context.match = None

                    return result, [((0, len(data)), (0, len(result)))], colorpos
                changed, result = _replace_parts(
                    replace_func, fields, field_idxs, context
                )
            elif pat.replace is not None:
                def replace_func(data: str, index: int, offset: int):
                    return _pat_search_replace(pat, data, offset, context)
                changed, result = _replace_parts(
                    replace_func, fields, field_idxs, context
                )
            elif len(pat.replace_groups) != 0:
                def replace_func(data: str, index: int, offset: int):
                    return _replace_groups(pat, data, offset, context)
                changed, result = _replace_parts(
                    replace_func, fields, field_idxs, context
                )
            else:
                def set_changed(data: str, index: int, offset: int):
                    nonlocal changed
                    if pat.regex.search(data): # type: ignore
                        changed = True
                    return data, [], {}
                _, result = _replace_parts(set_changed, fields, field_idxs, context)
    else:
        if field_idxs is None or len(field_idxs) != 0:
            changed, result = _replace_fields(pat, fields, context)

    context.fields = []

    return changed, result

def _replace_parts(
    replace_func: typing.Callable[
        [str, int, int],
        typing.Tuple[
            str,
            typing.List[ReplaceRange],
            ColorPositions
        ]
    ],
    parts: typing.Sequence[str],
    part_idxs: typing.Sequence[int],
    context: Context,
) -> typing.Tuple[bool, str]:
    """Replaces string by parts

    Args:
        replace_func (function): Replace function called on each part to be replaced
        parts (Sequence): List of string parts
        part_idxs (Sequence): List of part indicies that the replace function will be called on
        context (Context): Context

    Returns:
        tuple: Returns true if a match was found, and the new string
    """
    result = ''
    offset = 0
    changed = False

    def inner_replace_func(idx: int):
        context.field_cur = parts[idx]
        context.color_positions_end_idx = offset

        returnval = replace_func(parts[idx], idx, offset)

        context.field_cur = None
        context.color_positions_end_idx = -1
        return returnval

    for idx in range(len(parts)): # pylint: disable=consider-using-enumerate
        if idx not in part_idxs:
            result += parts[idx]
            offset += len(parts[idx])
            continue

        replaced, replace_ranges, colorpos = inner_replace_func(idx)
        if len(replace_ranges) != 0:
            changed = True

        _offset_replace_ranges(replace_ranges, offset)
        offset_color_positions(colorpos, offset)

        newcolorpos = update_color_positions_replace_ranges(
            context.color_positions,
            replace_ranges
        )
        context.color_positions.clear()
        context.color_positions.update(newcolorpos)

        update_color_positions(context.color_positions, colorpos)
        result += replaced
        offset += len(replaced)

    return changed, result

def _replace_fields(
    pat: Pattern,
    fields: typing.List[str],
    context: Context
) -> typing.Tuple[bool, str]:
    """Replaces fields

    Args:
        pat (Pattern): Pattern to apply
        fields (list): Fields
        context (dict): Context

    Returns:
        tuple: Returns true if a match was found, and the new string
    """
    def replace_field(data: str, index: int, offset: int):
        def idx_to_sep(x):
            return x * 2 - (3 * (x // 2))

        if (index & 1) == 0:
            result = _get_replace_field(
                fields,
                pyformat.fieldsep.idx_to_num(index),
                pat.replace_fields
            )
        else:
            if isinstance(pat.replace_fields, dict):
                result = _get_replace_field_separator(
                    idx_to_sep(index),
                    pat.replace_fields
                )
            else:
                result = None
        if result is None:
            return data, [], {}

        formatter = Formatter(context=context)
        result, colorpos = formatter.format_string(result)
        return result, [((0, len(data)), (0, len(result)))], colorpos

    return _replace_parts(replace_field, fields, range(0, len(fields)), context)

def _replace_groups(
    pat: Pattern,
    data: str,
    offset: int,
    context: Context
) -> typing.Tuple[
    str,
    typing.List[ReplaceRange],
    ColorPositions
]:
    """Replaces groups

    Args:
        pat (Pattern): Pattern to apply
        data (str): Input data
        offset (int): Offset this was called from
        context (dict): Context

    Returns:
        tuple: Returns true if a match was found, and the new string
    """
    orig_color_positions = context.copy_color_positions()
    color_positions: ColorPositions = {}
    replace_ranges = []

    def replace_group(match: typing.Match, idx: int, offset_inner: int) -> str:
        replace_val = _get_replace_group(match, idx, pat.replace_groups)
        if replace_val is None:
            return match.group(idx)

        context.match = match
        context.match_cur = match.group(idx)
        context.color_positions_end_idx = offset + match.start(idx)

        formatter = Formatter(context=context)
        replace_val, colorpos = formatter.format_string(replace_val)

        context.match = None
        context.match_cur = None

        offset_color_positions(colorpos, match.start(idx) - offset_inner)
        update_color_positions(color_positions, colorpos)
        update_color_positions(context.color_positions, colorpos)

        replace_ranges.append((
            match.span(idx),
            (match.start(idx) - offset_inner, match.start(idx) - offset_inner + len(replace_val))
        ))
        return replace_val

    if pat.regex is None:
        raise ValueError()

    newdata = _match_all_group_replace(pat.regex, data, replace_group)
    context.color_positions = orig_color_positions

    return newdata, replace_ranges, color_positions

def _match_all_group_replace(
    regex: typing.Pattern,
    string: str,
    replace_func: typing.Callable[[typing.Match, int, int], str]
) -> str:
    """Replace groups in regex matches in a string

    Args:
        regex (Pattern): Regex pattern
        string (str): String to match with pattern
        replace_func (function): Replace function to call on each group

    Returns:
        str: String with replaced values
    """
    result = ''
    last = 0

    def inner_replace_func(match: typing.Match, index: int, offset: int) -> str:
        return replace_func(match, index, offset - len(result))

    for match in regex.finditer(string):
        result += string[last:match.start()]
        result += match_group_replace(match, inner_replace_func)
        last = max(match.end(), last)

    result += string[last:]
    return result

def _pat_search_replace(
    pattern: Pattern,
    string: str,
    offset: int,
    context: Context
) -> typing.Tuple[
    str,
    typing.List[ReplaceRange],
    ColorPositions
]:
    """Regex pattern search and replace

    Args:
        pat (Pattern): Pattern to apply
        string (str): Input string
        offset (int): Offset this was called from
        context (dict): Context

    Returns:
        tuple: New string, replace ranges, and color positions
    """
    color_positions: ColorPositions = {}

    def replacer(match: typing.Match) -> str:
        context.color_positions_end_idx = offset + match.start()
        context.match = match

        if pattern.replace is None:
            context.match = None
            raise ValueError()

        formatter = Formatter(context=context)
        newstring, colorpos = formatter.format_string(pattern.replace)

        context.match = None

        offset_color_positions(colorpos, match.start())
        update_color_positions(color_positions, colorpos)
        return newstring

    if pattern.regex is None:
        raise ValueError()

    newstring, replace_ranges = search_replace(pattern.regex, string, replacer)
    return newstring, replace_ranges, color_positions

def _offset_replace_ranges(
    replace_ranges: typing.List[ReplaceRange],
    offset: int
) -> typing.List[ReplaceRange]:
    if offset == 0:
        return replace_ranges

    for ridx in range(len(replace_ranges)): #pylint: disable=consider-using-enumerate
        old_range, new_range = replace_ranges[ridx]
        replace_ranges[ridx] = (
            (old_range[0] + offset, old_range[1] + offset),
            (new_range[0] + offset, new_range[1] + offset),
        )
    return replace_ranges

def _get_replace_field(
    fields: typing.List[str],
    field_idx: int,
    replace_fields: typing.Union[
        ReplaceGroup,
        typing.List[str]
    ]
) -> typing.Optional[str]:
    """Gets the replace field value

    Args:
        fields (list): Fields
        field_idx (int): Index of field
        replace_fields (ReplaceGroup): Replace group

    Returns:
        str: Replace field value that matches
    """
    if isinstance(replace_fields, dict):
        return _get_group_value(
            pyformat.fieldsep.idx_to_num(len(fields)),
            replace_fields,
            field_idx
        )
    if isinstance(replace_fields, list) and field_idx <= len(replace_fields):
        return replace_fields[field_idx - 1]
    return None

def _get_replace_field_separator(
    field_sep_idx: int,
    replace_fields: ReplaceGroup
) -> typing.Optional[str]:
    """Gets the replace field separator value

    Args:
        field_sep_idx (int): Index of field separator
        replace_fields (ReplaceGroup): Replace group

    Returns:
        str: Replace field value that matches
    """
    for key, val in replace_fields.items():
        for part in str(key).split(','):
            try:
                if part[0] == 's' and int(part[1:]) == field_sep_idx:
                    return val
            except ValueError:
                pass
    return None

def _get_replace_group(
    match: typing.Match,
    idx: int,
    replace_groups: typing.Union[
        ReplaceGroup,
        typing.List[str]
    ]
) -> typing.Optional[str]:
    """Gets the replace group value

    Args:
        match (Match): Regex match
        idx (int): Index of match
        replace_groups (ReplaceGroup): Replace group

    Returns:
        str: Replace group value that matches
    """
    if isinstance(replace_groups, dict):
        val = replace_groups.get(str(idx))
        if val is not None:
            return val

        group = get_named_group_at_index(match, idx)
        if group is not None:
            if group in replace_groups:
                return replace_groups[group]
            for key in replace_groups:
                if group in str(key).split(','):
                    return replace_groups[key]

        return _get_group_value(len(match.groups()), replace_groups, idx)
    if isinstance(replace_groups, list) and idx <= len(replace_groups):
        return replace_groups[idx - 1]
    return None

def _get_group_value(
    grouplen,
    obj: ReplaceGroup,
    num: int
) -> typing.Optional[str]:
    """Gets the group value by number

    Args:
        grouplen (int): Length of group
        obj (ReplaceGroup): Replace group
        num (int): Number to match

    Returns:
        str: ReplaceGroup value that the index matches
    """
    for key, val in obj.items():
        for part in str(key).split(','):
            try:
                start, end, step = pyformat.fieldsep.get_range(part, grouplen)
                if num in range(start, end + 1, step):
                    return val
            except ValueError:
                pass
    return None
