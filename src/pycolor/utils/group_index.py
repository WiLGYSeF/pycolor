import typing

def get_named_group_index_dict(match: typing.Match) -> typing.Dict[int, str]:
    """Get the name/index map of the groups

    Args:
        match (Match): The regex match

    Returns:
        dict: A mapping of indices to names
    """
    group_idx_to_name = {}
    for group in match.groupdict():
        span = match.span(group)
        for i in range(1, len(match.groups()) + 1):
            if match.span(i) == span:
                group_idx_to_name[i] = group
                break

    return group_idx_to_name

def get_named_group_index_list(match: typing.Match) -> typing.List[typing.Optional[str]]:
    """Get the names of the groups

    Args:
        match (Match): The regex match

    Returns:
        list: The names of the groups by index
    """
    group_names: typing.List[typing.Optional[str]] = [None] * (len(match.groups()) + 1)

    for i in range(1, len(match.groups()) + 1):
        span = match.span(i)
        for group in match.groupdict():
            if match.span(group) == span:
                group_names[i] = group
                break

    return group_names

def get_named_group_index(match: typing.Match, name: str) -> typing.Optional[int]:
    """Get the index of the named group

    Args:
        match (Match): The regex match
        name (str): The group name

    Returns:
        int: The index of the group
    """
    if name in match.groupdict():
        span = match.span(name)
        for i in range(1, len(match.groups()) + 1):
            if match.span(i) == span:
                return i
    return None

def get_named_group_at_index(match: typing.Match, idx: int) -> typing.Optional[str]:
    """Get the name of the group

    Args:
        match (Match): The regex match
        idx (int): The group index

    Returns:
        str: The group name
    """
    if len(match.groups()) >= idx:
        span = match.span(idx)
        for group in match.groupdict():
            if match.span(group) == span:
                return group
    return None
