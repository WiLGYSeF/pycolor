import typing

def re_split(sep_regex: typing.Optional[typing.Pattern], string: str) -> typing.Iterable[str]:
    """Split a string with a regex separator

    Args:
        sep_regex (Pattern): The separator pattern
        string (str): The string to split

    Returns:
        list: The list of split parts
    """
    if sep_regex is None:
        yield string
        return

    last = 0
    for match in sep_regex.finditer(string):
        yield string[last:match.start()]
        yield string[match.start():match.end()]
        last = match.end()

    yield string[last:]
