import re
from typing import Pattern


def re_split(sep, string):
    if sep is None:
        return [ string ]

    regex = sep if isinstance(sep, Pattern) else re.compile(sep)

    result = []
    last = 0

    for match in regex.finditer(string):
        result.append(string[last:match.start()])
        result.append(string[match.start():match.end()])
        last = match.end()

    result.append(string[last:])
    return result
