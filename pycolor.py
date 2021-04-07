#!/usr/bin/env python3

import argparse
import os
import sys

from args import get_my_args, get_arg
from execute import read_stream
from pycolor_class import Pycolor


PYCOLOR_CONFIG_DIR = os.path.join(os.getenv('HOME'), '.pycolor')
PYCOLOR_CONFIG_DEFAULT = os.path.join(os.getenv('HOME'), '.pycolor.json')


def main(args, stdin_stream=sys.stdin):
    my_args, cmd_args = get_my_args(args)

    read_stdin = False
    if len(cmd_args) == 0:
        if not stdin_stream.isatty():
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
        load_config_files(pycobj, PYCOLOR_CONFIG_DIR)

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
        read_input_stream(pycobj, stdin_stream)
        sys.exit(0)

    returncode = pycobj.execute(cmd_args, profile=profile)
    sys.exit(returncode)

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


if __name__ == '__main__': #pragma: no cover
    main(sys.argv, stdin_stream=sys.stdin)
