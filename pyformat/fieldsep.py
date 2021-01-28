CHAR_SEPARATOR = 's'


def get_fields(formatter, context):
    last_field_num = idx_to_num(len(context['fields']))

    if formatter[0] == CHAR_SEPARATOR:
        return get_join_field(int(formatter[1:]), context)

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
            if end >= len(context['fields']):
                end = len(context['fields']) - 1
    else:
        number = int(number)
        if number < 0:
            number += last_field_num + 1

        start = num_to_idx(number)
        end = start

    if start > end:
        return ''

    newstring = context['fields'][start]
    for i in range(start + 2, end + 1, 2):
        if sep is None:
            newstring += context['fields'][i - 1] + context['fields'][i]
        else:
            newstring += sep + context['fields'][i]

    return newstring.decode('utf-8')

def get_join_field(num, context):
    if num < 0:
        num += idx_to_num(len(context['fields'])) + 1
    if num <= 1:
        return ''

    num = num_to_idx(num - 1) + 1
    if num >= len(context['fields']):
        return ''
    return context['fields'][num].decode('utf-8')

def idx_to_num(idx):
    return idx // 2 + 1

def num_to_idx(num):
    return (num - 1) * 2
