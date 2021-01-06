import re


def search_replace(pattern, string, replace, ignore_ranges=None, start_occurrance=1, max_count=-1):
    if ignore_ranges is None:
        ignore_ranges = []
    start_occurrance = max(1, start_occurrance)

    newstring = string[:0] #str or bytes
    count = 0
    replace_count = 0
    last = 0
    replace_ranges = []

    if isinstance(pattern, re._pattern_type):
        regex = pattern
    else:
        regex = re.compile(pattern)

    if not callable(replace):
        repl = replace
        replace = lambda x: repl

    igidx = 0

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

        if count >= start_occurrance and (max_count < 0 or replace_count < max_count):
            repl = replace(match)
            replace_count += 1
        else:
            repl = string[match.start():match.end()]

        newstring += string[last:match.start()] + repl
        last = match.end()

        start = match.start()
        end = match.start() + len(repl)

        for rng in replace_ranges:
            old_range, new_range = rng
            diff = new_range[1] - old_range[1] - (new_range[0] - old_range[0])
            start += diff
            end += diff

        replace_ranges.append((
            match.span(),
            (start, end)
        ))

    return newstring + string[last:], replace_ranges

def update_ranges(ranges, replace_ranges):
    for ridx in range(len(ranges)): #pylint: disable=consider-using-enumerate
        cur = ranges[ridx]
        start, end = cur

        for replidx in range(len(replace_ranges) - 1, -1, -1):
            old_range, new_range = replace_ranges[replidx]

            if cur[0] >= old_range[1]:
                diff = new_range[1] - old_range[1] - (new_range[0] - old_range[0])
                start += diff
                end += diff

        ranges[ridx] = (start, end)

    ranges.extend(map(lambda x: x[1], replace_ranges))
    ranges.sort(key=lambda x: x[0])
