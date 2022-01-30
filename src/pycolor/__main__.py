#!/usr/bin/env python3

import json
import os
import shutil
import sys
import typing

from . import __version__
from . import arguments
from . import config
from .execute.execute import read_stream
from .pycolor import pyformat
from .pycolor.pycolor_class import Pycolor
from .utils import debug_colors
from .utils.printmsg import printerr, is_color_enabled

CONFIG_DIR: typing.Optional[str] = None
CONFIG_DEFAULT: typing.Optional[str] = None

HOME = os.getenv('USERPROFILE' if os.name == 'nt' else 'HOME')

if HOME is not None:
    CONFIG_DIR = os.path.join(HOME, '.pycolor.d')
    CONFIG_DEFAULT = os.path.join(HOME, '.pycolor.json')

def main_args() -> None:
    main(sys.argv[1:])

def main(
    args: typing.List[str],
    stdout_stream: typing.TextIO = sys.stdout,
    stderr_stream: typing.TextIO = sys.stderr,
    stdin_stream: typing.TextIO = sys.stdin
) -> None:
    parser, argspace, cmd_args = arguments.get_args(args)
    read_stdin = len(cmd_args) == 0 or argspace.stdin

    if (
        config.SAMPLE_CONFIG_DIR is not None
        and CONFIG_DIR is not None
        and os.path.isdir(config.SAMPLE_CONFIG_DIR)
        and not os.path.exists(CONFIG_DIR)
    ):
        shutil.copytree(config.SAMPLE_CONFIG_DIR, CONFIG_DIR)

    if argspace.version:
        print(__version__)
        sys.exit(0)

    if argspace.debug_color:
        debug_colors.debug_colors()
        sys.exit(0)

    if argspace.debug_format:
        print(pyformat.fmt_str(
            argspace.debug_format + ('%Cz' if argspace.debug_format_reset else ''),
            color_enabled=is_color_enabled(argspace.color)
        ))
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
        execv=argspace.execv,
        stdout=stdout_stream,
        stderr=stderr_stream
    )

    if len(argspace.load_file) == 0:
        if CONFIG_DEFAULT is not None and os.path.isfile(CONFIG_DEFAULT):
            try_load_file(pycobj, CONFIG_DEFAULT)
        if CONFIG_DIR is not None and os.path.exists(CONFIG_DIR):
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
    if argspace.nobuffer:
        override_profile_conf(pycobj, 'nobuffer', argspace.nobuffer)

    profile = None
    if argspace.profile is not None:
        if len(argspace.profile) != 0:
            profile = pycobj.get_profile_by_name(argspace.profile)
        else:
            profile = pycobj.profile_default
        if profile is None:
            printerr('profile with name "%s" not found' % argspace.profile)
            sys.exit(1)

    if read_stdin:
        if profile is None and len(cmd_args) != 0:
            profile = pycobj.get_profile_by_command(cmd_args[0], cmd_args[1:])

        if profile is not None:
            pycobj.debug_print(1, 'using profile "%s"', profile.get_name())

            try:
                profile.load_patterns()
            except config.ConfigError as cex:
                printerr(cex)
                sys.exit(1)

        pycobj.current_profile = profile
        if len(cmd_args) == 0 and pycobj.is_default_profile():
            parser.print_help()
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

def read_input_stream(pycobj: Pycolor, stream: typing.TextIO) -> None:
    while True:
        if read_stream(stream, pycobj.stdout_cb, stream.read().encode()) is None:
            break
    read_stream(stream, pycobj.stdout_cb, b'', last=True)

def override_profile_conf(pycobj: Pycolor, attr: str, val: str) -> None:
    for prof in pycobj.profiles:
        setattr(prof, attr, val)
    setattr(pycobj.profile_default, attr, val)

def load_config_files(pycobj: Pycolor, path: str) -> None:
    # https://stackoverflow.com/a/3207973
    _, _, filenames = next(os.walk(path))

    for fname in sorted(filenames):
        filepath = os.path.join(path, fname)
        if os.path.isfile(filepath):
            try_load_file(pycobj, filepath)

def try_load_file(pycobj: Pycolor, fname: str) -> bool:
    try:
        pycobj.load_file(fname)
        return True
    except json.decoder.JSONDecodeError as jde:
        printerr(jde, filename=fname)
    except config.ConfigError as cex:
        printerr(cex, filename=fname)
    except Exception as err:
        printerr(err, filename=fname)
    return False

if __name__ == '__main__': #pragma: no cover
    main_args()
