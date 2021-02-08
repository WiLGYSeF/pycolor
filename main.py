import os
import sys

from execute import read_stream
from pycolor_class import Pycolor


PYCOLOR_CONFIG_DIR = os.path.join(os.getenv('HOME'), '.pycolor')
PYCOLOR_CONFIG_DEFAULT = os.path.join(os.getenv('HOME'), '.pycolor.json')


def main():
    my_args, cmd_args = get_my_args(sys.argv)

    read_stdin = False
    if len(cmd_args) == 0:
        if not sys.stdin.isatty():
            read_stdin = True
        else:
            sys.exit(1)

    pycobj = Pycolor()
    load_files = []
    profile_name = None

    for arg in my_args:
        argname, argval = get_arg(arg)
        if argname == 'color':
            if argval is None:
                argval = 'auto'
            pycobj.color_mode = argval
        elif argname == 'load-file':
            if argval is None:
                raise Exception()
            load_files.append(argval)
        elif argname == 'profile':
            if argval is None:
                raise Exception()
            profile_name = argval

    if os.path.isfile(PYCOLOR_CONFIG_DEFAULT):
        pycobj.load_file(PYCOLOR_CONFIG_DEFAULT)

    if os.path.exists(PYCOLOR_CONFIG_DIR):
        # https://stackoverflow.com/a/3207973
        _, _, filenames = next(os.walk(PYCOLOR_CONFIG_DIR))

        for fname in sorted(filenames):
            fpath = os.path.join(PYCOLOR_CONFIG_DIR, fname)
            if os.path.isfile(fpath):
                pycobj.load_file(fpath)

    for fname in load_files:
        pycobj.load_file(fname)

    profile = None
    if profile_name is not None:
        profile = pycobj.get_profile_by_name(profile_name)
        if profile is None:
            print('ERROR: profile with name "%s" not found' % profile_name, file=sys.stderr)
            sys.exit(1)

    if read_stdin:
        if profile is None:
            print('ERROR: no profile selected with --profile', file=sys.stderr)
            sys.exit(1)

        pycobj.set_current_profile(profile)

        while True:
            result = read_stream(
                sys.stdin.buffer,
                pycobj.stdout_cb,
                buffer_line=profile.buffer_line
            )
            if result is None:
                break

        read_stream(
            sys.stdin.buffer,
            pycobj.stdout_cb,
            buffer_line=profile.buffer_line,
            last=True
        )
        sys.exit(0)

    returncode = pycobj.execute(cmd_args, profile=profile)
    sys.exit(returncode)

def get_my_args(argv, start_idx=1):
    my_args = []
    cmd_args = []

    idx = start_idx
    while idx < len(argv):
        arg = argv[idx]
        if arg == '--':
            idx += 1
            break
        if not arg.startswith('--'):
            break

        my_args.append(arg)
        idx += 1

    while idx < len(argv):
        cmd_args.append(argv[idx])
        idx += 1

    return my_args, cmd_args

def get_arg(string, default=None):
    if not string.startswith('--'):
        raise ValueError()

    idx = string.find('=')
    if idx == -1:
        return string[2:], default

    return string[2:idx], string[idx + 1:]


if __name__ == '__main__': #pragma: no cover
    main()
