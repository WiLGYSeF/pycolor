#!/usr/bin/env python3

import argparse
import os
import sys

from execute import read_stream
from pycolor_class import Pycolor


CONFIG_DEFAULT_NAME = '.pycolor.json'
CONFIG_DIR = os.path.join(os.getenv('HOME'), '.pycolor.d')
CONFIG_DEFAULT = os.path.join(os.getenv('HOME'), CONFIG_DEFAULT_NAME)


def main(args, stdout_stream=sys.stdout, stderr_stream=sys.stderr, stdin_stream=sys.stdin):
    parser = argparse.ArgumentParser(
        description='do real-time output coloring and formatting of programs',
        usage='%(prog)s [options] COMMAND ARG ...'
    )
    parser.add_argument('--color',
        action='store', default='auto', nargs='?',
        choices=['auto', 'always', 'never', 'on', 'off'],
        help='enable/disable coloring output. if auto is selected, color will be enabled for'
        + ' terminal output but disabled on output redirection. on=always, off=never (default auto)'
    )
    parser.add_argument('--load-file',
        action='append', metavar='FILE', default=[],
        help='use this config file containing profiles'
    )
    parser.add_argument('--profile',
        action='store', metavar='NAME',
        help='specifically use this profile even if it does not match the current arguments'
    )
    parser.add_argument('-t', '--timestamp',
        action='store', metavar='FORMAT', default=False, nargs='?',
        help='force enable "timestamp" for all profiles with an optional FORMAT'
    )
    parser.add_argument('--less',
        action='store', metavar='PATH', default=False, nargs='?',
        help='force enable "less_output" for all profiles with an optional PATH to the less binary'
    )
    parser.add_argument('-v', '--verbose',
        action='count', default=0,
        help='enable debug mode to assist in configuring profiles'
    )
    parser.add_argument('--execv',
        action='store_true', default=True,
        help='use execv() if no profile matches the given command (default)'
    )
    parser.add_argument('--no-execv',
        dest='execv', action='store_false',
        help='do not use execv() if no profile matches the given command'
    )
    parser.add_argument('--tty',
        action='store_true', default=False,
        help='run the command in a pseudo-terminal'
    )
    parser.add_argument('--no-tty',
        dest='tty', action='store_false',
        help='do not run the command in a pseudo-terminal (default)'
    )

    argspace, cmd_args = parse_known_args(parser, args)

    read_stdin = len(cmd_args) == 0

    pycobj = Pycolor(color_mode=argspace.color, debug=argspace.verbose, execv=argspace.execv)
    pycobj.stdout = stdout_stream
    pycobj.stderr = stderr_stream

    if len(argspace.load_file) == 0:
        if os.path.isfile(CONFIG_DEFAULT):
            pycobj.load_file(CONFIG_DEFAULT)
        if os.path.exists(CONFIG_DIR):
            load_config_files(pycobj, CONFIG_DIR)
    else:
        for fname in argspace.load_file:
            pycobj.load_file(fname)

    if argspace.timestamp is not False:
        if argspace.timestamp is None:
            argspace.timestamp = True
        override_profile_conf(pycobj, 'timestamp', argspace.timestamp)

    if argspace.less is not False:
        if argspace.less is None:
            argspace.less = True
        override_profile_conf(pycobj, 'less_output', argspace.less)

    if argspace.tty:
        override_profile_conf(pycobj, 'tty', argspace.tty)

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

    #if os.geteuid() == 0:
    #    sys.exit(1)

    returncode = pycobj.execute(cmd_args, profile=profile)
    sys.exit(returncode)

def parse_known_args(parser, args):
    argspace, cmd_args = parser.parse_known_args(args)
    if len(cmd_args) != 0 and cmd_args[0] == '--':
        cmd_args = cmd_args[1:]

    is_consecutive, argidx = consecutive_end_args(args, cmd_args)
    if not is_consecutive:
        argspace = parser.parse_args(args[:argidx])
        cmd_args = args[argidx:]
    return argspace, cmd_args

def consecutive_end_args(args, subset):
    lenarg = len(args)
    lensub = len(subset)

    if lensub == 0:
        return True, lenarg
    if lenarg < lensub:
        return False, -1

    for i in range(lenarg):
        if args[i] != subset[0]:
            continue

        startidx = i
        off = 1
        i += 1
        while i < lenarg and off < lensub:
            if args[i] != subset[off]:
                return False, startidx
            off += 1
            i += 1
        return i == lenarg and off == lensub, startidx
    return False, lenarg

def read_input_stream(pycobj, stream):
    while True:
        if read_stream(stream.buffer, pycobj.stdout_cb) is None:
            break
    read_stream(stream.buffer, pycobj.stdout_cb, last=True)

def override_profile_conf(pycobj, attr, val):
    for prof in pycobj.profiles:
        setattr(prof, attr, val)
    setattr(pycobj.profile_default, attr, val)

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
    main(sys.argv[1:])
