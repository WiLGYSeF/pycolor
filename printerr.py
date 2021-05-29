import sys

import pyformat


def printerr(*args, **kwargs):
    color = kwargs.get('color')
    filename = kwargs.get('filename')
    prefix = kwargs.get('prefix', True)
    sep = kwargs.get('sep', ' ')

    use_color = is_color_enabled(color)

    for key in (
        'color',
        'filename',
        'prefix',
        'sep'
    ):
        if key in kwargs:
            del kwargs[key]

    string = sep.join(map(lambda x: str(x), args))

    if filename:
        if use_color:
            string = '%s: %s' % (
                pyformat.format_string('%Cly') + filename + pyformat.format_string('%Cz'),
                string
            )
        else:
            string = filename + ': ' + string

    if prefix:
        if use_color:
            string = '%s: %s' % (
                pyformat.format_string('%Clr') + 'error' + pyformat.format_string('%Cz'),
                string
            )
        else:
            string = 'error: ' + string

    print(string, **kwargs, file=sys.stderr)

def is_color_enabled(color):
    if color in (True, 'always', 'on', '1'):
        return True
    if color in (False, 'never', 'off', '0'):
        return False
    return sys.stdout.isatty()
