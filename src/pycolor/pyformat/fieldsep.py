import typing

CHAR_SEPARATOR = 's'

def get_field_range(number: str, length: int) -> typing.Tuple[int, int, int]:
    last_field_num = idx_to_num(length)

    if '*' not in number:
        start = int(number)
        if start < 0:
            start += last_field_num + 1
        start = num_to_idx(start)
        return start, start, 1

    rangespl = number.split('*')
    start_str = rangespl[0]
    end_str = rangespl[1]
    step = int(rangespl[2]) if len(rangespl) >= 3 else 1

    start = num_to_idx(int(start_str) if len(start_str) != 0 else 1)

    if len(end_str) != 0:
        end = int(end_str)
        if end < 0:
            end += last_field_num + 1
        end = min(num_to_idx(end), length)
    else:
        end = length

    return start, end, step

def get_fields(formatter: str, context: dict) -> str:
    fields = context['fields']
    if formatter[0] == CHAR_SEPARATOR:
        return get_join_field(int(formatter[1:]), fields)

    comma_idx = formatter.find(',')
    if comma_idx != -1:
        number = formatter[:comma_idx]
        sep = formatter[comma_idx + 1:]
    else:
        number = formatter
        sep = None

    start, end, _ = get_field_range(number, len(fields))
    if start > end or start >= len(fields):
        return ''

    string = fields[start]
    for i in range(start + 2, end + 1, 2):
        string += (fields[i - 1] if sep is None else sep) + fields[i]
    return string

def get_join_field(num: int, fields: typing.List[str]) -> str:
    """Get the separator value at num

    Args:
        fields (list): Field values and separators

    Returns:
        string: The field separator value at num
    """
    if num < 0:
        num += idx_to_num(len(fields)) + 1
    if num <= 1:
        return ''

    num = num_to_idx(num - 1) + 1
    return fields[num] if num < len(fields) else ''

def idx_to_num(idx: int) -> int:
    return idx // 2 + 1

def num_to_idx(num: int) -> int:
    return (num - 1) * 2
