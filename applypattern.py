from colorpositions import update_color_positions, offset_color_positions
from group_index import get_named_group_at_index
from match_group_replace import match_group_replace
import pyformat
from search_replace import search_replace, update_positions
from split import re_split


def apply_pattern(pat, linenum, data, context):
    if not pat.is_active(linenum, data):
        return False, None
    if pat.super_regex is not None and not pat.super_regex.search(data):
        return False, None

    color_positions = context['color']['positions']
    context = pyformat.dictcopy(context)
    context['string'] = data

    if pat.separator_regex is not None:
        fields = re_split(pat.separator_regex, data)
        field_idxs = pat.get_field_indexes(fields)
        context['fields'] = fields

    if pat.separator_regex is None or all([
        pat.field is not None,
        pat.field == 0,
        len(field_idxs) != 0
    ]):
        if pat.replace_all is not None:
            match = pat.regex.search(data)
            if match is None:
                return False, None

            context['match'] = match
            context['idx'] = match.start()

            data, colorpos = pyformat.format_string(
                pat.replace_all,
                context=context,
                return_color_positions=True
            )
            color_positions.clear()
            color_positions.update(colorpos)
            return True, data

        if pat.replace is not None:
            data, replace_ranges, colorpos = pat_schrep(pat, data, context)
            if len(replace_ranges) == 0:
                return False, None

            update_positions(color_positions, replace_ranges)
            update_color_positions(color_positions, colorpos)
            return True, data

        if 'fields' in context and all([
            len(pat.replace_fields) != 0,
            len(field_idxs) != 0
        ]):
            newdata = ''
            changed = False
            offset = 0
            choffset = 0
            replace_ranges = []
            field_idx = 0

            for idx in range(0, len(fields) + 1, 2):
                replace_val = get_replace_field(fields, field_idx, pat.replace_fields)
                sep = fields[idx + 1] if idx != len(fields) - 1 else ''

                if replace_val is None:
                    replace_val = fields[idx]

                context['field_cur'] = fields[idx]
                replace_val, colorpos = pyformat.format_string(
                    replace_val,
                    context=context,
                    return_color_positions=True
                )

                colorpos = offset_color_positions(colorpos, offset)
                choffset += len(replace_val) - len(fields[idx])

                update_positions(colorpos, replace_ranges)
                replace_ranges.append((
                    (offset, offset + len(fields[idx])),
                    (
                        offset + choffset,
                        offset + choffset + len(replace_val)
                    )
                ))
                update_color_positions(color_positions, colorpos)

                newdata += replace_val + sep
                offset += len(replace_val) + len(sep)
                field_idx += 1

            return changed, newdata

        if len(pat.replace_groups) != 0:
            choffset = 0
            replace_ranges = []

            def replace_group(match, idx):
                nonlocal choffset

                replace_val = get_replace_group(match, idx, pat.replace_groups)

                if replace_val is None:
                    return match.group(idx)

                context['match'] = match
                context['idx'] = match.start()
                context['match_cur'] = match.group(idx)

                replace_val, colorpos = pyformat.format_string(
                    replace_val,
                    context=context,
                    return_color_positions=True
                )

                colorpos = offset_color_positions(colorpos, match.start(idx))
                choffset += len(replace_val) - (match.end(idx) - match.start(idx))

                update_positions(colorpos, replace_ranges)
                replace_ranges.append((
                    match.span(idx),
                    (
                        match.start(idx) + choffset,
                        match.start(idx) + choffset + len(replace_val)
                    )
                ))

                update_color_positions(color_positions, colorpos)
                return replace_val

            newdata = match_group_replace(pat.regex, data, replace_group)
            return 'match' in context, newdata
        return pat.regex.search(data), data

    if pat.replace_all is not None:
        for field_idx in field_idxs:
            match = pat.regex.search(fields[field_idx])
            if match is None:
                continue

            context['match'] = match
            context['idx'] = match.start()

            data, colorpos = pyformat.format_string(
                pat.replace_all,
                context=context,
                return_color_positions=True
            )

            color_positions.clear()
            color_positions.update(colorpos)
            return True, data

    if pat.replace is not None:
        matched = False
        for field_idx in field_idxs:
            newfield, replace_ranges, colorpos = pat_schrep(pat, fields[field_idx], context)
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

    for field_idx in field_idxs:
        match = pat.regex.search(fields[field_idx])
        if match is not None:
            return True, data

    return False, None

def pat_schrep(pattern, string, context):
    color_positions = {}
    ctx = pyformat.dictcopy(context)

    def replacer(match):
        ctx['string'] = string
        ctx['idx'] = match.start()
        ctx['match'] = match

        newstring, colorpos = pyformat.format_string(
            pattern.replace,
            context=ctx,
            return_color_positions=True
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

def get_replace_field(fields, field_idx, replace_fields):
    if isinstance(replace_fields, dict):
        return _get_field_range(fields, replace_fields, field_idx)
    if isinstance(replace_fields, list) and field_idx < len(replace_fields):
        return replace_fields[field_idx]
    return None

def get_replace_group(match, idx, replace_groups):
    if isinstance(replace_groups, dict):
        val = replace_groups.get(str(idx))
        if val is not None:
            return val

        group = get_named_group_at_index(match, idx)
        if group is not None:
            return replace_groups.get(group)

        return _get_field_range(match.groups(), replace_groups, idx - 1)
    if isinstance(replace_groups, list) and idx <= len(replace_groups):
        return replace_groups[idx - 1]
    return None

def _get_field_range(fields, obj, idx):
    for key, val in obj.items():
        for num in key.split(','):
            try:
                start, end, step = pyformat.fieldsep.get_field_range(num, fields)
                start = pyformat.fieldsep.idx_to_num(start)
                end = pyformat.fieldsep.idx_to_num(end)

                if idx in range(start - 1, end, step):
                    return val
            except ValueError:
                pass
    return None
