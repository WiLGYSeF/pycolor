import sys

from pycolor_class import Pycolor


PYCOLOR_CONFIG_FNAME = 'config.json'


def main():
    argcount = 1
    while argcount < len(sys.argv):
        arg = sys.argv[argcount]
        if arg == '--' or not arg.startswith('--'):
            break

        argcount += 1
    argcount -= 1

    if argcount == len(sys.argv) - 1:
        print('no command')
        exit(1)

    args = sys.argv[1:argcount + 1]

    pycobj = Pycolor()
    cmd_args = sys.argv[argcount + 1:]

    for arg in args:
        if arg.startswith('--color'):
            _, argval = get_arg(arg, 'auto')
            pycobj.color_mode = argval

    pycobj.load_file(PYCOLOR_CONFIG_FNAME)

    returncode = pycobj.execute(cmd_args)
    sys.exit(returncode)

def get_arg(string, default=None):
    if not string.startswith('--'):
        raise ValueError()

    idx = string.find('=')
    if idx == -1:
        return string[2:], default

    return string[2:idx], string[idx + 1:]
