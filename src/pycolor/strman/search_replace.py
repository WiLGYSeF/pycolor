import re
import typing

Span = typing.Tuple[int, int]
ReplaceRange = typing.Tuple[Span, Span]

def search_replace(
    pattern: typing.Union[typing.Pattern, str],
    string: typing.AnyStr,
    replace: typing.Union[typing.Callable[[typing.Match], typing.AnyStr], typing.AnyStr],
    **kwargs
) -> typing.Tuple[typing.AnyStr, typing.List[ReplaceRange]]:
    """Search and replace in string

    Args:
        pattern (Pattern): Search pattern
        string (str): String to search and replace in
        replace: Value to replace with

        ignore_ranges (list): Do not replace matches in these ranges
        start_occurrence (int): Start replacing when finding the nth occurrence
        max_count (int): Replace at most this many occurrences (-1 is all)

    Returns:
        tuple: New string and the ranges replaced
    """
    ignore_ranges: typing.List[Span] = kwargs.get('ignore_ranges', [])
    start_occurrence: int = max(kwargs.get('start_occurrence', 1), 1)
    max_count: int = kwargs.get('max_count', -1)

    regex = pattern if isinstance(pattern, typing.Pattern) else re.compile(pattern)
    replf: typing.Callable[[typing.Match], typing.AnyStr] = (
        replace if callable(replace) else lambda x: replace # type: ignore
    )

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
            if any((
                match.start() >= ign[0] and match.start() < ign[1],
                ign[0] >= match.start() and ign[0] < match.end()
            )):
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
        if last == len(string):
            break

    newstring += string[last:]
    return newstring, replace_ranges
