import re


def search_replace(pattern, string, replace, ignore_ranges=None, start_occurrence=1, max_count=-1):
    if ignore_ranges is None:
        ignore_ranges = []
    start_occurrence = max(1, start_occurrence)

    newstring = string[:0] #str or bytes
    count = 0
    replace_count = 0
    last = 0
    replace_ranges = []

    if isinstance(pattern, re._pattern_type):
        regex = pattern
    else:
        regex = re.compile(pattern)

    if callable(replace):
        replf = replace
    else:
        replf = lambda x: replace

    igidx = 0
    replace_diff = 0

    for match in regex.finditer(string):
        while igidx < len(ignore_ranges) and ignore_ranges[igidx][1] < match.start():
            igidx += 1

        if igidx < len(ignore_ranges):
            ign = ignore_ranges[igidx]
            if any([
                match.start() >= ign[0] and match.start() < ign[1],
                ign[0] >= match.start() and ign[0] < match.end()
            ]):
                continue

        count += 1

        if count >= start_occurrence and (max_count < 0 or replace_count < max_count):
            replace_string = replf(match)
            newstring += string[last:match.start()] + replace_string

            start = match.start() + replace_diff
            end = match.start() + len(replace_string) + replace_diff
            replace_diff = end - match.end()

            replace_ranges.append((
                match.span(),
                (start, end)
            ))
            replace_count += 1
        else:
            newstring += string[last:match.end()]
        last = match.end()

    return newstring + string[last:], replace_ranges

def update_ranges(ranges, replace_ranges):
    for ridx in range(len(ranges)): #pylint: disable=consider-using-enumerate
        cur = ranges[ridx]
        start, end = cur

        for old_range, new_range in replace_ranges:
            if old_range[1] > cur[0]:
                break

            diff = new_range[1] - old_range[1] - (new_range[0] - old_range[0])
            start += diff
            end += diff

        ranges[ridx] = (start, end)

    ranges.extend(map(lambda x: x[1], replace_ranges))
    ranges.sort(key=lambda x: x[0])

def update_positions(positions, replace_ranges):
    for key in sorted(positions.keys(), reverse=True):
        newkey = key

        for old_range, new_range in replace_ranges:
            if old_range[1] > key:
                break

            newkey += new_range[1] - old_range[1] - (new_range[0] - old_range[0])

        if newkey != key:
            positions[newkey] = positions[key]
            del positions[key]
