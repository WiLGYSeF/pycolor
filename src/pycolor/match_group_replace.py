import re
import typing

def match_group_replace_one(
    match: re.Match,
    replace_func: typing.Callable[[re.Match, int], str]
) -> str:
    """Replace groups in match

    Args:
        match (Match): Regex match
        replace_func (function): Takes the match and group index, returns replacement string

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
        result += replace_func(match, idx, match.start(idx) - len(result) - offset)
        last = max(match.end(idx) - match.start(0), last)
    result += string[last:]

    return result

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
        result += match_group_replace_one(match, replace_func, len(result))
        last = max(match.end(0), last)

    result += string[last:]
    return result
