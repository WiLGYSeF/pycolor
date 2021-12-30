import re
import typing

from .colorpositions import update_color_positions, offset_color_positions
from .config.pattern import Pattern
from .group_index import get_named_group_at_index
from .match_group_replace import match_group_replace
from . import pyformat
from .search_replace import search_replace, ReplaceRange
from .split import re_split

def apply_pattern(pat: Pattern, data: str, context: dict) -> typing.Tuple[bool, typing.Optional[str]]:
    if pat.super_regex is not None and not pat.super_regex.search(data):
        return False, None

    color_positions = context['color']['positions']
    context['string'] = data
    for key in ['field', 'match', 'field_cur', 'match_cur', 'idx']:
        if key in context:
            del context[key]

    fields: typing.List[str] = []
    field_idxs: range = range(0)

    if pat.separator_regex is not None:
        fields = list(re_split(pat.separator_regex, data))
        field_idxs = pat.get_field_indexes(len(fields))
        context['fields'] = fields

    if pat.separator_regex is None or all((
        pat.field == 0,
        len(field_idxs) != 0
    )):
        if pat.regex is not None:
            if pat.replace_all is not None:
                match = pat.regex.search(data)
                if match is None:
                    return False, None

                context['match'] = match
                context['idx'] = match.start()

                data, colorpos = pyformat.format_string(
                    pat.replace_all,
                    context=context
                )
                color_positions.clear()
                color_positions.update(colorpos)
                return True, data

            if pat.replace is not None:
                data, replace_ranges, colorpos = _pat_schrep(pat, data, context)
                if len(replace_ranges) == 0:
                    return False, None

                update_positions(color_positions, replace_ranges)
                update_color_positions(color_positions, colorpos)
                return True, data

        if 'fields' in context and all((
            len(pat.replace_fields) != 0,
            len(field_idxs) != 0,
        )):
            return _replace_fields(pat, data, fields, color_positions, context)

        if len(pat.replace_groups) != 0:
            return _replace_groups(pat, data, color_positions, context)

        if pat.regex is not None:
            return bool(pat.regex.search(data)), data
        return False, data

    if pat.regex is not None:
        if pat.replace_all is not None:
            for field_idx in field_idxs:
                match = pat.regex.search(fields[field_idx])
                if match is None:
                    continue

                context['match'] = match
                context['idx'] = match.start()

                data, colorpos = pyformat.format_string(
                    pat.replace_all,
                    context=context
                )

                color_positions.clear()
                color_positions.update(colorpos)
                return True, data

        if pat.replace is not None:
            matched = False
            for field_idx in field_idxs:
                newfield, replace_ranges, colorpos = _pat_schrep(pat, fields[field_idx], context)
                if len(replace_ranges) == 0:
                    continue
                fields[field_idx] = newfield
                matched = True

                offset = 0
                for i in range(field_idx):
                    offset += len(fields[i])

                for idx in range(len(replace_ranges)): #pylint: disable=consider-using-enumerate
                    old_range, new_range = replace_ranges[idx]
                    replace_ranges[idx] = (
                        (old_range[0] + offset, old_range[1] + offset),
                        (new_range[0] + offset, new_range[1] + offset),
                    )

                if offset > 0:
                    for key in sorted(colorpos.keys(), reverse=True):
                        colorpos[key + offset] = colorpos[key]
                        del colorpos[key]

                update_positions(color_positions, replace_ranges)
                update_color_positions(color_positions, colorpos)
            if not matched:
                return False, None
            return True, ''.join(fields)

    if 'fields' in context and all((
        len(pat.replace_fields) != 0,
        len(field_idxs) != 0,
    )):
        return _replace_fields(pat, data, fields, color_positions, context)

    if pat.regex is not None:
        for field_idx in field_idxs:
            match = pat.regex.search(fields[field_idx])
            if match is not None:
                return True, data

    return False, None

def _replace_fields(
    pat: Pattern,
    data: str,
    fields: typing.List[str],
    color_positions: typing.Dict[int, str],
    context: dict
) -> typing.Tuple[bool, str]:
    replace_ranges = []
    colorpos_arr = []
    original_color_positions = color_positions.copy()
    newdata = ''
    changed = False
    offset = 0
    origin_offset = 0
    field_idx = 0

    for idx in range(0, len(fields) + 1, 2):
        replace_val = get_replace_field(fields, field_idx, pat.replace_fields)
        sep = fields[idx + 1] if idx != len(fields) - 1 else ''

        if replace_val is None:
            replace_val = fields[idx]
        else:
            changed = True

        context['field_cur'] = fields[idx]
        context['idx'] = len(newdata)

        replace_val, colorpos = pyformat.format_string(
            replace_val,
            context=context
        )

        colorpos = offset_color_positions(colorpos, offset)
        colorpos_arr.append(colorpos)
        update_color_positions(color_positions, colorpos)

        replace_ranges.append((
            (
                origin_offset,
                origin_offset + len(fields[idx])
            ),
            (
                offset,
                offset + len(replace_val)
            )
        ))

        newdata += replace_val + sep
        offset += len(replace_val) + len(sep)
        origin_offset += len(fields[idx]) + len(sep)
        field_idx += 1

    color_positions.clear()
    color_positions.update(original_color_positions)

    update_positions(color_positions, replace_ranges)
    for colorpos in colorpos_arr:
        update_color_positions(color_positions, colorpos)

    return changed, newdata

def _replace_groups(
    pat: Pattern,
    data: str,
    color_positions: typing.Dict[int, str],
    context: dict
) -> typing.Tuple[bool, str]:
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
            (
                match.start(idx) - offset,
                match.start(idx) - offset + len(replace_val)
            )
        ))
        return replace_val

    newdata = match_group_replace(pat.regex, data, replace_group)
    color_positions.clear()
    color_positions.update(original_color_positions)

    update_positions(color_positions, replace_ranges)
    for colorpos in colorpos_arr:
        update_color_positions(color_positions, colorpos)

    return 'match' in context, newdata

def _pat_schrep(
    pattern: Pattern,
    string: str,
    context: dict
) -> typing.Tuple[
    str,
    typing.List[ReplaceRange],
    typing.Dict[int, str]
]:
    color_positions: typing.Dict[int, str] = {}

    def replacer(match: re.Match) -> str:
        context['string'] = string
        context['idx'] = match.start()
        context['match'] = match

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
        typing.Dict[str, str],
        typing.List[str]
    ]
) -> typing.Optional[str]:
    if isinstance(replace_fields, dict):
        return _get_field_range(fields, replace_fields, field_idx)
    if isinstance(replace_fields, list) and field_idx < len(replace_fields):
        return replace_fields[field_idx]
    return None

def get_replace_group(
    match: re.Match,
    idx: int,
    replace_groups: typing.Union[
        typing.Dict[str, str],
        typing.List[str]
    ]
) -> typing.Optional[str]:
    if isinstance(replace_groups, dict):
        val = replace_groups.get(str(idx))
        if val is not None:
            return val

        group = get_named_group_at_index(match, idx)
        if group is not None:
            if group in replace_groups:
                return replace_groups[group]
            for key in replace_groups:
                if group in key.split(','):
                    return replace_groups[key]

        return _get_group_range(match.groups(), replace_groups, idx)
    if isinstance(replace_groups, list) and idx <= len(replace_groups):
        return replace_groups[idx - 1]
    return None

def _get_range(number: str, length: int) -> range:
    spl = number.split('*')

    start = int(spl[0]) if len(spl[0]) != 0 else 1
    if start >= length:
        return range(start, start + 1)
    while start < 0:
        start += length

    if len(spl) >= 2:
        if len(spl[1]) > 0:
            end = min(int(spl[1]), length)
        else:
            end = length
    else:
        end = start
    while end < 0:
        end += length

    return range(start, end + 1, int(spl[2]) if len(spl) >= 3 else 1)

def _get_group_range(
    groups: typing.Sequence[str],
    obj: typing.Dict[str, str],
    idx: int
) -> typing.Optional[str]:
    for key, val in obj.items():
        for num in key.split(','):
            try:
                if idx in _get_range(num, len(groups)):
                    return val
            except ValueError:
                pass
    return None

def _get_field_range(
    fields: typing.Sequence[str],
    obj: typing.Dict[str, str],
    idx: int
) -> typing.Optional[str]:
    for key, val in obj.items():
        for num in key.split(','):
            try:
                start, end, step = pyformat.fieldsep.get_field_range(num, len(fields))
                start = pyformat.fieldsep.idx_to_num(start)
                end = pyformat.fieldsep.idx_to_num(end)
                if idx in range(start - 1, end, step):
                    return val
            except ValueError:
                pass
    return None
