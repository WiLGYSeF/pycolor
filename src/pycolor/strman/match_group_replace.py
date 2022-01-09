import re
import typing

def match_group_replace(
    match: re.Match,
    replace_func: typing.Callable[[re.Match, int, int], str]
) -> str:
    """Replace groups in match

    Args:
        match (Match): Regex match
        replace_func (function): Takes the match, group index, and replace offset, returns replacement string

    Returns:
        str: Replaced string result
    """
    string = match.group(0)
    result = ''
    last = 0

    for idx in range(1, len(match.groups()) + 1):
        if match.start(idx) == -1:
            continue
        result += string[last:match.start(idx) - match.start(0)]
        result += replace_func(match, idx, match.start(idx) - len(result))
        last = max(match.end(idx) - match.start(0), last)
    result += string[last:]

    return result
