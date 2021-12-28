import sys
import typing

from . import pyformat

FMT_RESET = pyformat.format_string('%Cz')

def printmsg(*args, **kwargs) -> None:
    color: typing.Union[str, bool, None]  = kwargs.get('color')
    filename: typing.Optional[str] = kwargs.get('filename')
    prefix: bool = kwargs.get('prefix', True)
    prefix_color: str = kwargs.get('prefix_color', '')
    sep: str = kwargs.get('sep', ' ')

    use_color = is_color_enabled(color)

    for key in (
        'color',
        'filename',
        'prefix',
        'prefix_color',
        'sep'
    ):
        if key in kwargs:
            del kwargs[key]

    string = sep.join(map(lambda x: str(x), args))

    if filename:
        if use_color:
            string = '%s: %s' % (
                pyformat.format_string('%Cly') + filename + FMT_RESET,
                string
            )
        else:
            string = filename + ': ' + string

    if prefix:
        if use_color:
            string = '%s: %s' % (
                pyformat.format_string(prefix_color) + prefix + FMT_RESET,
                string
            )
        else:
            string =  '%s: %s' % (prefix, string)

    print(string, **kwargs, file=sys.stderr)

def printerr(*args, **kwargs) -> None:
    new_kwargs = kwargs
    new_kwargs['prefix'] = 'error'
    new_kwargs['prefix_color'] = '%Clr'
    printmsg(*args, **new_kwargs)

def printwarn(*args, **kwargs) -> None:
    new_kwargs = kwargs
    new_kwargs['prefix'] = 'warn'
    new_kwargs['prefix_color'] = '%Cly'
    printmsg(*args, **new_kwargs)

def is_color_enabled(color: typing.Union[str, bool, None]) -> bool:
    if color in (True, 'always', 'on', '1'):
        return True
    if color in (False, 'never', 'off', '0'):
        return False
    return sys.stdout.isatty()
