CHAR_SEPARATOR = 's'


def get_fields(formatter, context):
    fields = context['fields']
    last_field_num = idx_to_num(len(fields))

    if formatter[0] == CHAR_SEPARATOR:
        return get_join_field(int(formatter[1:]), fields)

    comma_idx = formatter.find(',')
    if comma_idx != -1:
        number = formatter[:comma_idx]
        sep = formatter[comma_idx + 1:]
    else:
        number = formatter
        sep = None

    if '*' in number:
        rangespl = number.split('*')
        start = rangespl[0]
        end = rangespl[1]

        if len(start) == 0:
            start = num_to_idx(1)
        else:
            start = num_to_idx(int(start))

        if len(end) == 0:
            end = len(fields)
        else:
            end = int(end)
            if end < 0:
                end += last_field_num + 1
            end = num_to_idx(end)
            if end >= len(fields):
                end = len(fields) - 1
    else:
        number = int(number)
        if number < 0:
            number += last_field_num + 1

        start = num_to_idx(number)
        end = start

    if start > end or start >= len(fields):
        return ''

    string = fields[start]
    for i in range(start + 2, end + 1, 2):
        if sep is None:
            string += fields[i - 1] + fields[i]
        else:
            string += sep + fields[i]

    return string

def get_join_field(num, fields):
    if num < 0:
        num += idx_to_num(len(fields)) + 1
    if num <= 1:
        return ''

    num = num_to_idx(num - 1) + 1
    return fields[num] if num < len(fields) else ''

def idx_to_num(idx):
    return idx // 2 + 1

def num_to_idx(num):
    return (num - 1) * 2
