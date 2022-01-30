import sys
import typing

from ..pycolor import pyformat

FMT_RESET = pyformat.fmt_str('%Cz')

def printmsg(*args, **kwargs) -> None:
    color: typing.Union[str, bool, None]  = kwargs.get('color')
    filename: typing.Optional[str] = kwargs.get('filename')
    prefix: typing.Optional[str] = kwargs.get('prefix')
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
                pyformat.fmt_str('%Cly') + filename + FMT_RESET,
                string
            )
        else:
            string = '%s: %s' % (filename, string)

    if prefix:
        if use_color:
            string = '%s: %s' % (
                pyformat.fmt_str(prefix_color) + prefix + FMT_RESET,
                string
            )
        else:
            string =  '%s: %s' % (prefix, string)

    print(string, **kwargs, file=sys.stderr)

def printerr(*args, **kwargs) -> None:
    printmsg(*args, prefix='error', prefix_color='%Clr', **kwargs)

def printwarn(*args, **kwargs) -> None:
    printmsg(*args, prefix='warn', prefix_color='%Cly', **kwargs)

def is_color_enabled(color: typing.Union[str, bool, None]) -> bool:
    if color in (True, 'always', 'on', '1'):
        return True
    if color in (False, 'never', 'off', '0'):
        return False
    return sys.stdout.isatty()
