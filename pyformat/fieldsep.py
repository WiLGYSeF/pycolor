def get_fields(formatter, context):
    last_field_num = idx_to_num(len(context['fields']))

    if formatter[0] == 'e':
        field_idx = int(formatter[1:])
        if field_idx < 0:
            field_idx += last_field_num + 1
        field_idx = num_to_idx(field_idx - 1) + 1

        if field_idx >= len(context['fields']):
            return ''
        return context['fields'][field_idx].decode('utf-8')

    indexes = set()

    comma_idx = formatter.find(',')
    if comma_idx != -1:
        number = formatter[:comma_idx]
        sep = formatter[comma_idx + 1:].encode('utf-8')
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
            end = len(context['fields'])
        else:
            end = int(end)
            if end < 0:
                end += last_field_num + 1
            end = num_to_idx(end)

        for i in range(start, end + 1):
            indexes.add(i)
    else:
        number = int(number)
        if number < 0:
            number += last_field_num + 1
        indexes.add(num_to_idx(number))

    indexes = sorted(indexes)
    if len(indexes) == 0:
        return ''

    newstring = context['fields'][indexes[0]]

    for i in range(2, len(indexes), 2):
        if indexes[i] >= len(context['fields']):
            break

        if sep is None:
            newstring += context['fields'][indexes[i - 1]] + context['fields'][indexes[i]]
        else:
            newstring += sep + context['fields'][indexes[i]]

    return newstring.decode('utf-8')

def idx_to_num(idx):
    return idx // 2 + 1

def num_to_idx(num):
    return (num - 1) * 2
