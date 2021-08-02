import re
from typing import Pattern


def search_replace(pattern, string, replace, **kwargs):
    """Search and replace in string

    Args:
        pattern (Pattern): The search pattern
        string (str): The string to search and replace in
        replace: The value to replace with

        ignore_ranges (list): Do not replace matches in these ranges
        start_occurrence (int): Start replacing when finding the nth occurrence
        max_count (int): Replace at most this many occurrences (-1 is all)

    Returns:
        tuple: The new string and the ranges replaced
    """
    ignore_ranges = kwargs.get('ignore_ranges', [])
    start_occurrence = kwargs.get('start_occurrence', 1)
    max_count = kwargs.get('max_count', -1)

    start_occurrence = max(1, start_occurrence)

    regex = pattern if isinstance(pattern, Pattern) else re.compile(pattern)
    replf = replace if callable(replace) else lambda x: replace

    newstring = string[:0] #str or bytes
    count = 0
    replace_count = 0
    last = 0
    replace_ranges = []

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

    newstring += string[last:]
    return newstring, replace_ranges
