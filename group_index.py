def get_named_group_index_dict(match):
    group_idx_to_name = {}
    for group in match.groupdict():
        span = match.span(group)
        for i in range(1, len(match.groups()) + 1):
            if match.span(i) == span:
                group_idx_to_name[i] = group
                break

    return group_idx_to_name

def get_named_group_index_list(match):
    group_names = [None] * (len(match.groups()) + 1)

    for i in range(1, len(match.groups()) + 1):
        span = match.span(i)
        for group in match.groupdict():
            if match.span(group) == span:
                group_names[i] = group
                break

    return group_names

def get_named_group_index(match, name):
    if name in match.groupdict():
        span = match.span(name)
        for i in range(1, len(match.groups()) + 1):
            if span == match.span(i):
                return i
    return None

def get_named_group_at_index(match, idx):
    if len(match.groups()) >= idx:
        span = match.span(idx)
        for group in match.groupdict():
            if match.span(group) == span:
                return group
    return None
