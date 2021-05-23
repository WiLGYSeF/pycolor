import re
from typing import Pattern


def match_group_replace(pattern, string, replace_func):
    result = ''
    last = 0

    regex = pattern if isinstance(pattern, Pattern) else re.compile(pattern)

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
