#!/usr/bin/env python3

import argparse
import os
import sys

from execute import read_stream
from pycolor_class import Pycolor


PYCOLOR_CONFIG_DIR = os.path.join(os.getenv('HOME'), '.pycolor')
PYCOLOR_CONFIG_DEFAULT = os.path.join(os.getenv('HOME'), '.pycolor.json')


def main(args, stdin_stream=sys.stdin):
    parser = argparse.ArgumentParser(
        description='do real-time output coloring and formatting of programs',
        usage='%(prog)s [options] COMMAND ARG ...'
    )
    parser.add_argument('--color',
        action='store', default='auto', nargs='?',
        choices=['auto', 'always', 'never', 'on', 'off'],
        help='enable/disable coloring output. if auto is selected, color will be enabled for terminal output but disabled on output redirection. on=always, off=never (default auto)'
    )
    parser.add_argument('--load-file',
        action='append', metavar='FILE', default=[],
        help='load config file containing profiles'
    )
    parser.add_argument('--profile',
        action='store', metavar='NAME',
        help='specifically use this profile even if it does not match the current arguments'
    )

    argspace, cmd_args = parser.parse_known_args(args)
    if cmd_args[0] == '--':
        cmd_args = cmd_args[1:]
    if not consecutive_end_args(args, cmd_args):
        parser.print_help()
        sys.exit(1)

    read_stdin = False
    if len(cmd_args) == 0:
        if not stdin_stream.isatty():
            read_stdin = True
        else:
            sys.exit(1)

    pycobj = Pycolor(color_mode=argspace.color)

    if os.path.isfile(PYCOLOR_CONFIG_DEFAULT):
        pycobj.load_file(PYCOLOR_CONFIG_DEFAULT)

    if os.path.exists(PYCOLOR_CONFIG_DIR):
        load_config_files(pycobj, PYCOLOR_CONFIG_DIR)

    for fname in argspace.load_file:
        pycobj.load_file(fname)

    profile = None
    if argspace.profile is not None:
        profile = pycobj.get_profile_by_name(argspace.profile)
        if profile is None:
            printerr('ERROR: profile with name "%s" not found' % argspace.profile)
            sys.exit(1)

    if read_stdin:
        if profile is None:
            printerr('ERROR: no profile selected with --profile')
            sys.exit(1)

        pycobj.set_current_profile(profile)
        read_input_stream(pycobj, stdin_stream)
        sys.exit(0)

    returncode = pycobj.execute(cmd_args, profile=profile)
    sys.exit(returncode)

def consecutive_end_args(args, subset):
    lensub = len(subset)
    if lensub == 0:
        return True
    lenarg = len(args)
    if lenarg < lensub:
        return False

    for i in range(lenarg):
        if args[i] != subset[0]:
            continue

        off = 1
        i += 1
        while i < lenarg and off < lensub:
            if args[i] != subset[off]:
                return False
            off += 1
            i += 1
        return i == lenarg and off == lensub
    return False

def read_input_stream(pycobj, stream):
    while True:
        result = read_stream(
            stream.buffer,
            pycobj.stdout_cb,
            buffer_line=pycobj.current_profile.buffer_line
        )
        if result is None:
            break

    read_stream(
        stream.buffer,
        pycobj.stdout_cb,
        buffer_line=pycobj.current_profile.buffer_line,
        last=True
    )

def load_config_files(pycobj, path):
    # https://stackoverflow.com/a/3207973
    _, _, filenames = next(os.walk(path))

    for fname in sorted(filenames):
        filepath = os.path.join(path, fname)
        if os.path.isfile(filepath):
            pycobj.load_file(filepath)

def printerr(*args):
    print(*args, file=sys.stderr)


if __name__ == '__main__': #pragma: no cover
    main(sys.argv[1:], stdin_stream=sys.stdin)
