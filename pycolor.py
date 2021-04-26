#!/usr/bin/env python3

import os
import sys

import arguments
import debug_colors
from execute import read_stream
from pycolor_class import Pycolor
import pyformat


CONFIG_DEFAULT_NAME = '.pycolor.json'
CONFIG_DIR = os.path.join(os.getenv('HOME'), '.pycolor.d')
CONFIG_DEFAULT = os.path.join(os.getenv('HOME'), CONFIG_DEFAULT_NAME)


def main(args, stdout_stream=sys.stdout, stderr_stream=sys.stderr, stdin_stream=sys.stdin):
    argspace, cmd_args = arguments.get_args(args)

    if argspace.debug_color:
        debug_colors.debug_colors()
        sys.exit(0)

    if argspace.debug_format:
        print(pyformat.format_string(argspace.debug_format + '%Cz'))
        sys.exit(0)

    read_stdin = len(cmd_args) == 0 or argspace.debug_from_stdin

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
        if profile is None and len(cmd_args) != 0:
            profile = pycobj.get_profile_by_command(cmd_args[0], cmd_args[1:])
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
