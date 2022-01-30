import datetime
import os
from shutil import which
import sys
import typing

from ..config.profile import Profile
from ..execute import execute
from ..utils.printmsg import printerr
from . import pyformat
from .applypattern import apply_pattern
from .profileloader import ProfileLoader
from .pyformat.coloring.colorpositions import insert_color_data, extract_color_data
from .pyformat.coloring.colorstate import ColorState
from .pyformat.context import Context

FMT_DEBUG = pyformat.fmt_str('%Cz%Cde')
FMT_RESET = pyformat.fmt_str('%Cz')

TIMESTAMP_DEFAULT = '%Y-%m-%d %H:%M:%S: '

class Pycolor:
    def __init__(self, **kwargs):
        """
        0 - no debug
        1 - print received data
        2 - print written data
        3 - print after each pattern applied
        4 - print line numbers before received data
        """
        self.debug: int = kwargs.get('debug', 0)
        self.debug_log: typing.Optional[str] = kwargs.get('debug_log', None)
        self.debug_log_out: bool = kwargs.get('debug_log_out', False)
        self.execv: bool = kwargs.get('execv', False)
        self.stdout: typing.TextIO = kwargs.get('stdout', sys.stdout)
        self.stderr: typing.TextIO = kwargs.get('stderr', sys.stderr)

        self._is_color_enabled: bool = False
        self.color_mode: str = kwargs.get('color_mode', 'auto')

        self.encoding = 'utf-8'

        self._debug_file: typing.TextIO = None
        if self.debug_log is not None:
            self._debug_file = self._open_debug_file(self.debug_log)

        self._profloader: ProfileLoader = ProfileLoader()
        self._current_profile: Profile = None

        self._linenum: int = 0

        self._color_state_orig: ColorState = ColorState()
        self._color_state: ColorState = self._color_state_orig.copy()

    def __del__(self):
        if self._debug_file is not None:
            self._debug_file.close()

    @property
    def profiles(self) -> typing.List[Profile]:
        return self._profloader.profiles

    @property
    def profile_default(self) -> Profile:
        return self._profloader.profile_default

    @property
    def color_mode(self) -> str:
        return self._color_mode

    @color_mode.setter
    def color_mode(self, val: str) -> None:
        self._color_mode = val

        mode = val.lower()
        if mode in ('always', 'on', '1'):
            self._is_color_enabled = True
        elif mode in ('never', 'off', '0'):
            self._is_color_enabled = False
        else:
            self._is_color_enabled = not self.is_being_redirected()

    @property
    def is_color_enabled(self) -> bool:
        return self._is_color_enabled

    @property
    def current_profile(self) -> typing.Optional[Profile]:
        return self._current_profile

    @current_profile.setter
    def current_profile(self, val: typing.Optional[Profile]) -> None:
        self._current_profile = val if val is not None else self._profloader.profile_default

    def load_file(self, fname: str) -> None:
        """Loads profiles from JSON file

        Args:
            fname (str): Filename
        """
        self._profloader.load_file(fname)

    def get_profile_by_name(self, name: str) -> typing.Optional[Profile]:
        """Gets loaded profile by name

        Args:
            name (str): Name of profile

        Returns:
            Profile: Profile with name, or None if not found
        """
        return self._profloader.get_profile_by_name(name)

    def get_profile_by_command(self,
        command: str,
        args: typing.List[str]
    ) -> typing.Optional[Profile]:
        """Gets the loaded profile by command and its arguments

        Args:
            command (str): Command being run
            args (list): Command arguments

        Returns:
            Profile: Last matching loaded profile, or null if not found
        """
        return self._profloader.get_profile_by_command(command, args)

    def is_default_profile(self) -> bool:
        """Checks if the profile is the default profile

        Args:
            profile (Profile): Profile to check

        Returns:
            bool: Returns true if the profile is the default profile
        """
        return self._profloader.is_default_profile(self._current_profile)

    def execute(self, cmd: typing.List[str], profile: Profile = None) -> int:
        """Executes the command

        Args:
            cmd (list): Command and arguments
            profile (Profile): Optional profile to use

        Returns:
            int: Return code of command
        """
        self.current_profile = (
            profile if profile is not None else self.get_profile_by_command(cmd[0], cmd[1:])
        )

        self._debug_write_line('running %s' % cmd)

        if self.is_default_profile() and self.debug == 0 and self.execv:
            cmd_path = which(cmd[0])
            if cmd_path is None:
                cmd_path = cmd[0]

            self._debug_write_line('calling os.execv(%s, %s)' % (cmd_path, cmd))

            try:
                os.execv(cmd_path, cmd)
            except FileNotFoundError:
                printerr("command '%s' not found" % cmd_path)
            sys.exit(1)

        self.debug_print(1, 'using profile "%s"', self._current_profile.get_name())

        self._current_profile.load_patterns()

        try:
            return execute.execute(
                cmd,
                self.stdout_cb,
                self.stderr_cb,
                tty=self._current_profile.tty,
                nobuffer=self._current_profile.nobuffer,
            )
        except FileNotFoundError:
            printerr("command '%s' not found" % cmd[0])
            sys.exit(1)

    def _data_callback(self, stream: typing.TextIO, data: str) -> None:
        """Internal data stream callback from executed command

        Args:
            stream (IOBase): Output stream
            data (str): Data from stream callback
        """
        removed_newline = False
        removed_carriagereturn = False

        self.debug_print(4, 'on line %d', self._linenum)
        # optimization to avoid encode()
        if self.debug >= 1:
            self.debug_print(1, 'received: %s', data.encode(self.encoding))

        data, color_positions = extract_color_data(data)
        if self._current_profile.remove_input_color:
            color_positions = {}

        if len(data) != 0 and data[-1] == '\n':
            self._linenum += 1
            data = data[:-1]
            removed_newline = True
        if len(data) != 0 and data[-1] == '\r':
            data = data[:-1]
            removed_carriagereturn = True

        context = Context(
            color_enabled = self._is_color_enabled,
            color_aliases = self._current_profile.color_aliases,
            color_positions = color_positions
        )
        do_filter = False

        for pat in self._current_profile.loaded_patterns:
            if any((
                not pat.enabled,
                pat.stdout_only and stream != self.stdout,
                pat.stderr_only and stream != self.stderr
            )):
                continue

            was_active = pat.active
            pat.is_active(self._linenum, data)

            if pat.active != was_active:
                self.debug_print(3,
                    '%s %s' % ('active:  ' if pat.active else 'inactive:', pat.from_profile_str)
                )
            if not pat.active:
                continue

            matched, applied = apply_pattern(pat, data, context)
            if matched:
                if pat.filter:
                    # optimization to avoid encode()
                    if self.debug >= 2:
                        self.debug_print(2, 'filtered: %s', data.encode(self.encoding))
                    do_filter = True
                    break

                if applied is not None:
                    # optimization to avoid encode() and insert_color_data()
                    if self.debug >= 3:
                        self.debug_print(3, 'apply%3s: %s',
                            pat.from_profile_str,
                            insert_color_data(
                                applied, context.color_positions
                            ).encode(self.encoding)
                        )
                    data = applied

                if pat.skip_others:
                    break

        if do_filter:
            return

        if len(context.color_positions) != 0:
            data = insert_color_data(data, context.color_positions)

        if removed_carriagereturn:
            data += '\r'
        if removed_newline:
            data += '\n'

        # optimization to avoid encode()
        if self.debug >= 2:
            self.debug_print(2, 'writing:  %s', data.encode(self.encoding))

        if self._current_profile.timestamp:
            self._write_timestamp(stream)

        stream.flush()
        stream.write(data)
        stream.flush()

        self._color_state.set(data)

    def _write_timestamp(self, stream: typing.TextIO) -> None:
        """Write timestamp to stream

        Args:
            stream (IOBase): Output stream
        """
        timestamp = TIMESTAMP_DEFAULT
        if isinstance(self._current_profile.timestamp, str):
            timestamp = self._current_profile.timestamp

        stream.write(self._color_state_orig.get_string(
            compare_state=self._color_state
        ))
        stream.write(datetime.datetime.strftime(datetime.datetime.now(), timestamp))
        stream.write(self._color_state.get_string(
            compare_state=self._color_state_orig
        ))

    def stdout_cb(self, data: str) -> None:
        self._data_callback(self.stdout, data)

    def stderr_cb(self, data: str) -> None:
        self._data_callback(self.stderr, data)

    def debug_print(self, lvl: int, val: str, *args) -> None:
        """Debug print

        Args:
            lvl (int): Debug level of print
            val (str): Debug string format
        """
        if self.debug < lvl:
            return

        if self.is_color_enabled:
            reset = FMT_DEBUG
            oldstate = str(self._color_state)
            if len(oldstate) == 0:
                oldstate = FMT_RESET
        else:
            reset = ''
            oldstate = ''

        msg = val % args

        if self._debug_file is not None:
            self._debug_write_line(msg)

        if self._debug_file is None or self.debug_log_out:
            print('%s    DEBUG%d: %s%s' % (reset, lvl, msg, oldstate))

    def _open_debug_file(self, fname: str) -> typing.TextIO:
        """Open the debug file for writing

        Args:
            fname (str): Debug filename

        Returns:
            TextIOWrapper: debug file
        """
        if self.debug == 0:
            self.debug = 1
        file_exists = os.path.isfile(fname)

        file = open(fname, 'a')
        if file_exists:
            file.write('\n')
        return file

    def _debug_write_line(self, line: str) -> None:
        """Write debug line to file

        Args:
            line (str): Debug string line
        """
        if self._debug_file is not None:
            self._debug_file.write('%s: %s\n' % (
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), line
            ))
            self._debug_file.flush()

    def is_being_redirected(self) -> bool:
        """Checks if the output is being sent to a terminal or being redirected/piped

        Returns:
            bool: Returns true if the output is being redirected/piped
        """
        return not self.stdout.isatty()
