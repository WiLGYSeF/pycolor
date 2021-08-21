#!/usr/bin/env python3

import json
import os
import sys

from . import arguments
from . import config
from . import debug_colors
from .execute import read_stream
from .printmsg import printerr, is_color_enabled
from .pycolor_class import Pycolor
from . import pyformat
from . import __version__


if os.name == 'nt':
    HOME = os.getenv('USERPROFILE')
else:
    HOME = os.getenv('HOME')
CONFIG_DIR = os.path.join(HOME, '.pycolor.d')
CONFIG_DEFAULT = os.path.join(HOME, '.pycolor.json')


def main_args():
    main(sys.argv[1:])

def main(args, stdout_stream=sys.stdout, stderr_stream=sys.stderr, stdin_stream=sys.stdin):
    argspace, cmd_args = arguments.get_args(args)
    read_stdin = len(cmd_args) == 0 or argspace.stdin

    if argspace.version:
        print(__version__)
        sys.exit(0)

    if argspace.debug_color:
        debug_colors.debug_colors()
        sys.exit(0)

    if argspace.debug_format:
        fmt = argspace.debug_format + ('%Cz' if argspace.debug_format_reset else '')
        print(pyformat.format_string(fmt, context={
            'color': {
                'enabled': is_color_enabled(argspace.color)
            }
        }))
        sys.exit(0)

    debug_log = None
    debug_log_out = False

    if argspace.debug_log:
        debug_log = argspace.debug_log
    if argspace.debug_log_out:
        debug_log = argspace.debug_log_out
        debug_log_out = True

    pycobj = Pycolor(
        color_mode=argspace.color,
        debug=argspace.verbose,
        debug_log=debug_log,
        debug_log_out=debug_log_out,
        execv=argspace.execv
    )
    pycobj.stdout = stdout_stream
    pycobj.stderr = stderr_stream

    if len(argspace.load_file) == 0:
        if os.path.isfile(CONFIG_DEFAULT):
            try_load_file(pycobj, CONFIG_DEFAULT)
        if os.path.exists(CONFIG_DIR):
            load_config_files(pycobj, CONFIG_DIR)
    else:
        for fname in argspace.load_file:
            try_load_file(pycobj, fname)

    if argspace.timestamp is not False:
        if argspace.timestamp is None:
            argspace.timestamp = True
        override_profile_conf(pycobj, 'timestamp', argspace.timestamp)

    if argspace.tty:
        override_profile_conf(pycobj, 'tty', argspace.tty)
    if argspace.interactive:
        override_profile_conf(pycobj, 'interactive', argspace.interactive)

    profile = None
    if argspace.profile is not None:
        if len(argspace.profile) != 0:
            profile = pycobj.get_profile_by_name(argspace.profile)
        else:
            profile = pycobj.profloader.profile_default
        if profile is None:
            printerr('profile with name "%s" not found' % argspace.profile)
            sys.exit(1)

    if read_stdin:
        if profile is None and len(cmd_args) != 0:
            profile = pycobj.get_profile_by_command(cmd_args[0], cmd_args[1:])

        if profile is not None:
            pycobj.debug_print(1, 'using profile "%s"', profile.get_name())

            try:
                # ensure patterns are loaded here first
                profile.loaded_patterns
            except config.ConfigError as cex:
                printerr(cex)
                sys.exit(1)

        pycobj.set_current_profile(profile)
        if len(cmd_args) == 0 and pycobj.profloader.is_default_profile(pycobj.current_profile):
            arguments._parser.print_help()
            sys.exit(1)

        try:
            read_input_stream(pycobj, stdin_stream)
        except KeyboardInterrupt:
            pass
        sys.exit(0)

    try:
        returncode = pycobj.execute(cmd_args, profile=profile)
        sys.exit(returncode)
    except config.ConfigError as cex:
        printerr(cex)
        sys.exit(1)

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
            try_load_file(pycobj, filepath)

def try_load_file(pycobj, fname):
    try:
        pycobj.load_file(fname)
        return True
    except json.decoder.JSONDecodeError as jde:
        printerr(jde, filename=fname)
    except config.ConfigError as cex:
        printerr(cex, filename=fname)
    return False

if __name__ == '__main__': #pragma: no cover
    main_args()
