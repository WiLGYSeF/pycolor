# TODO: cleanup

import re
import typing

from .colorpositions import update_color_positions, offset_color_positions
from .config.pattern import Pattern, ReplaceGroup
from .group_index import get_named_group_at_index
from . import pyformat
from .search_replace import search_replace, ReplaceRange
from .split import re_split

def apply_pattern(
    pat: Pattern,
    data: str,
    context: dict
) -> typing.Tuple[bool, typing.Optional[str]]:
    """Applies the pattern to the input

    Args:
        pat (Pattern): Pattern to apply
        data (str): Input data
        context (dict): Context

    Returns:
        tuple: Returns true if a match was found, and the new string
    """
    if pat.super_regex is not None and not pat.super_regex.search(data):
        return False, None

    color_positions = context['color']['positions']
    context['string'] = data
    for key in ['field', 'match', 'field_cur', 'match_cur', 'idx']:
        if key in context:
            del context[key]

    fields: typing.List[str] = []
    field_idxs: typing.Optional[typing.List[int]] = []

    if pat.separator_regex is not None:
        fields = list(re_split(pat.separator_regex, data))
        field_idxs = pat.get_field_indexes(len(fields))
        context['fields'] = fields

        if field_idxs is not None and len(field_idxs) == 0:
            return False, None
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
                def replace_func(data: str, index: int):
                    context['field_cur'] = fields[index]

                    match = pat.regex.search(data) # type: ignore
                    if match is None:
                        return data, [], {}

                    context['match'] = match
                    context['idx'] = match.start()

                    result, colorpos = pyformat.format_string(pat.replace_all, context=context) # type: ignore
                    return result, [((0, len(data)), (0, len(result)))], colorpos
                changed, result = _replace_parts(replace_func, fields, field_idxs, color_positions)
            elif pat.replace is not None:
                def replace_func(data: str, index: int):
                    context['field_cur'] = fields[index]
                    return _pat_schrep(pat, data, context)
                changed, result = _replace_parts(replace_func, fields, field_idxs, color_positions)
            elif len(pat.replace_groups) != 0:
                changed, result = _replace_groups(pat, data, color_positions, context)
            else:
                def set_changed(data: str, index: int):
                    nonlocal changed
                    if pat.regex.search(data): # type: ignore
                        changed = True
                    return data, [], {}
                _, result = _replace_parts(set_changed, fields, field_idxs, {})
    else:
        changed, result = _replace_fields(pat, fields, color_positions, context)

    return changed, result

def _replace_parts(
    replace_func: typing.Callable[
        [str, int],
        typing.Tuple[
            str,
            typing.List[ReplaceRange],
            typing.Dict[int, str]
        ]
    ],
    parts: typing.Sequence[str],
    part_idxs: typing.Sequence[int],
    color_positions: typing.Dict[int, str]
) -> typing.Tuple[bool, str]:
    result = ''
    offset = 0
    changed = False

    for idx in range(len(parts)): # pylint: disable=consider-using-enumerate
        if idx not in part_idxs:
            result += parts[idx]
            offset += len(parts[idx])
            continue

        replaced, replace_ranges, colorpos = replace_func(parts[idx], idx)
        if len(replace_ranges) != 0:
            changed = True

        if offset > 0:
            for ridx in range(len(replace_ranges)): #pylint: disable=consider-using-enumerate
                old_range, new_range = replace_ranges[ridx]
                replace_ranges[ridx] = (
                    (old_range[0] + offset, old_range[1] + offset),
                    (new_range[0] + offset, new_range[1] + offset),
                )
            for ckey in sorted(colorpos.keys(), reverse=True):
                colorpos[ckey + offset] = colorpos[ckey]
                del colorpos[ckey]

        update_positions(color_positions, replace_ranges)
        update_color_positions(color_positions, colorpos)
        result += replaced
        offset += len(parts[idx])

    return changed, result

def _replace_fields(
    pat: Pattern,
    fields: typing.List[str],
    color_positions: typing.Dict[int, str],
    context: dict
) -> typing.Tuple[bool, str]:
    """Replaces fields

    Args:
        pat (Pattern): Pattern to apply
        fields (list): Fields
        color_positions (dict): Color positions
        context (dict): Context

    Returns:
        tuple: Returns true if a match was found, and the new string
    """
    def replace_field(data: str, index: int):
        result = get_replace_field(fields, pyformat.fieldsep.idx_to_num(index), pat.replace_fields)
        if result is None:
            return data, [], {}

        context['field_cur'] = fields[index]
        # context['idx'] = len(newdata) # TODO: why

        result, colorpos = pyformat.format_string(result, context=context)
        return result, [((0, len(data)), (0, len(result)))], colorpos

    return _replace_parts(replace_field, fields, range(0, len(fields), 2), color_positions)

def _replace_groups(
    pat: Pattern,
    data: str,
    color_positions: typing.Dict[int, str],
    context: dict
) -> typing.Tuple[bool, str]:
    """Replaces fields

    Args:
        pat (Pattern): Pattern to apply
        data (str): Input data
        color_positions (dict): Color positions
        context (dict): Context

    Returns:
        tuple: Returns true if a match was found, and the new string
    """
    replace_ranges = []
    colorpos_arr = []
    original_color_positions = color_positions.copy()

    def replace_group(match: re.Match, idx: int, offset: int) -> str:
        replace_val = get_replace_group(match, idx, pat.replace_groups)
        if replace_val is None:
            return match.group(idx)

        context['match'] = match
        context['idx'] = match.start(idx)
        context['match_cur'] = match.group(idx)

        replace_val, colorpos = pyformat.format_string(
            replace_val,
            context=context
        )

        colorpos = offset_color_positions(colorpos, match.start(idx) - offset)
        colorpos_arr.append(colorpos)
        update_color_positions(color_positions, colorpos)

        replace_ranges.append((
            match.span(idx),
            (match.start(idx) - offset, match.start(idx) - offset + len(replace_val))
        ))
        return replace_val

    if pat.regex is None:
        raise ValueError()

    newdata = _match_group_replace(pat.regex, data, replace_group)
    color_positions.clear()
    color_positions.update(original_color_positions)

    update_positions(color_positions, replace_ranges)
    for colorpos in colorpos_arr:
        update_color_positions(color_positions, colorpos)

    return 'match' in context, newdata

def _match_group_replace(
    regex: typing.Pattern,
    string: str,
    replace_func: typing.Callable[[re.Match, int, int], str]
) -> str:
    # TODO: use match_group_replace in match_group_replace.py
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

    for match in regex.finditer(string):
        result += string[last:match.start(0)]
        last = max(match.start(0), last)

        for i in range(1, len(match.groups()) + 1):
            if match.start(i) == -1:
                continue
            result += string[last:match.start(i)]
            result += replace_func(match, i, match.start(i) - len(result))
            last = max(match.end(i), last)

        result += string[last:match.end(0)]
        last = max(match.end(0), last)

    result += string[last:]
    return result

def _pat_schrep(
    pattern: Pattern,
    string: str,
    context: dict
) -> typing.Tuple[
    str,
    typing.List[ReplaceRange],
    typing.Dict[int, str]
]:
    """Regex pattern search and replace

    Args:
        pat (Pattern): Pattern to apply
        string (str): Input string
        context (dict): Context

    Returns:
        tuple: New string, replace ranges, and color positions
    """
    color_positions: typing.Dict[int, str] = {}

    def replacer(match: re.Match) -> str:
        context['string'] = string
        context['idx'] = match.start()
        context['match'] = match

        if pattern.replace is None:
            raise ValueError()

        newstring, colorpos = pyformat.format_string(
            pattern.replace,
            context=context
        )

        if match.start() > 0:
            for key in sorted(colorpos.keys(), reverse=True):
                colorpos[key + match.start()] = colorpos[key]
                del colorpos[key]

        update_color_positions(color_positions, colorpos)
        return newstring

    if pattern.regex is None:
        raise ValueError()

    newstring, replace_ranges = search_replace(
        pattern.regex,
        string,
        replacer
    )
    return newstring, replace_ranges, color_positions

def update_positions(
    positions: typing.Dict[int, str],
    replace_ranges: typing.List[ReplaceRange]
) -> None:
    """Update color positions based on replace ranges

    Args:
        positions (dict): Color positions
        replace_ranges (list): Replace ranges
    """
    replace_ranges.sort(key=lambda x: x[0][0], reverse=True)

    for key in sorted(positions.keys(), reverse=True):
        newkey = key
        skip = False
        for old_range, new_range in replace_ranges:
            if old_range[1] < key:
                newkey += new_range[1] - old_range[1]
                break
            if old_range[0] < key and key < old_range[1]:
                if key - old_range[0] > new_range[1] - new_range[0]:
                    skip = True
                else:
                    # FIXME not sure how to handle this
                    # newkey += new_range[1] - old_range[1] - (new_range[0] - old_range[0])
                    skip = True
                break

        if not skip:
            if newkey != key:
                positions[newkey] = positions[key]
                del positions[key]
        else:
            del positions[key]

def get_replace_field(
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
        return _get_field_range(fields, replace_fields, field_idx)
    if isinstance(replace_fields, list) and field_idx <= len(replace_fields):
        return replace_fields[field_idx - 1]
    return None

def get_replace_group(
    match: re.Match,
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

        return _get_group_range(match.groups(), replace_groups, idx)
    if isinstance(replace_groups, list) and idx <= len(replace_groups):
        return replace_groups[idx - 1]
    return None

def _get_group_range(
    groups: typing.Sequence[str],
    obj: ReplaceGroup,
    idx: int
) -> typing.Optional[str]:
    """Gets the group range value

    Args:
        groups (list): Match groups
        obj (ReplaceGroup): Replace group
        idx (int): Group index to match

    Returns:
        str: ReplaceGroup value that the index matches
    """
    for key, val in obj.items():
        for num in str(key).split(','):
            try:
                start, end, step = pyformat.fieldsep.get_range(num, len(groups))
                if idx in range(start, end + 1, step):
                    return val
            except ValueError:
                pass
    return None

def _get_field_range(
    fields: typing.Sequence[str],
    obj: ReplaceGroup,
    idx: int
) -> typing.Optional[str]:
    """Gets the field range value

    Args:
        fields (list): Fields
        obj (ReplaceGroup): ReplaceGroup
        idx (int): Field index to match

    Returns:
        str: ReplaceGroup value that the index matches
    """
    for key, val in obj.items():
        for num in str(key).split(','):
            try:
                start, end, step = pyformat.fieldsep.get_range(
                    num,
                    pyformat.fieldsep.idx_to_num(len(fields))
                )
                if idx in range(start, end + 1, step):
                    return val
            except ValueError:
                pass
    return None
