import re
import typing

def match_group_replace(
    regex: typing.Pattern,
    string: str,
    replace_func: typing.Callable[[re.Match, int, int], str]
) -> str:
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
