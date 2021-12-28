import re
import typing

def re_split(sep: typing.Union[typing.Pattern, str], string: str) -> typing.List[str]:
    """Split a string with a regex separator

    Args:
        sep (Pattern): The separator pattern
        string (str): The string to split

    Returns:
        list: The list of split parts
    """
    if sep is None:
        return [ string ]

    regex = sep if isinstance(sep, typing.Pattern) else re.compile(sep)

    result = []
    last = 0

    for match in regex.finditer(string):
        result.append(string[last:match.start()])
        result.append(string[match.start():match.end()])
        last = match.end()

    result.append(string[last:])
    return result
