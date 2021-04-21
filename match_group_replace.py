import re
from typing import Pattern


def match_group_replace(pattern, string, replace_func):
    result = ''
    last = 0

    regex = pattern if isinstance(pattern, Pattern) else re.compile(pattern)

    for match in regex.finditer(string):
        result += string[last:match.start(0)]
        last = match.start(0)

        for i in range(1, len(match.groups()) + 1):
            result += string[last:match.start(i)] + replace_func(match, i)
            last = match.end(i)

        result += string[last:match.end(0)]
        last = match.end(0)

    result += string[last:]
    return result
