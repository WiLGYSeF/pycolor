import typing

CHAR_SEPARATOR = 's'

def get_range(string: str, length: int) -> typing.Tuple[int, int, int]:
    """Gets the range from string, starting from 1 to length

    Args:
        string (str): Range string
        length (int): Max length

    Returns:
        tuple: Returns start, end, and step
    """
    spl = string.split('*')
    start = int(spl[0]) if len(spl[0]) > 0 else 1
    end = min((int(spl[1]) if len(spl[1]) > 0 else length) if len(spl) >= 2 else start, length)
    step = (int(spl[2]) if len(spl[2]) > 0 else 1) if len(spl) >= 3 else 1

    while start < 0:
        start += length + 1
    while end < 0:
        end += length + 1

    return start, end, step

def get_fields(formatter: str, fields: typing.List[str]) -> str:
    """Gets the field string from formatter

    Args:
        formatter (str): Format string
        fields (list): Fields

    Returns:
        str: The concatenated fields
    """
    if formatter[0] == CHAR_SEPARATOR:
        return get_join_field(int(formatter[1:]), fields)

    comma_idx = formatter.find(',')
    if comma_idx != -1:
        number = formatter[:comma_idx]
        sep = formatter[comma_idx + 1:]
    else:
        number = formatter
        sep = None

    start, end, _ = get_range(number, idx_to_num(len(fields)))
    start = num_to_idx(start)
    end = num_to_idx(end)
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

    num = num_to_idx(num - 1) + 1
    return fields[num] if num >= 0 and num < len(fields) else ''

def idx_to_num(idx: int) -> int:
    return idx // 2 + 1

def num_to_idx(num: int) -> int:
    return (num - 1) * 2
