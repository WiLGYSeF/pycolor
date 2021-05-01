import datetime
import io
import os
import sys
import tempfile

from applypattern import apply_pattern
from colorpositions import insert_color_data
from colorstate import ColorState
import execute
from profileloader import ProfileLoader
import pyformat
from which import which


class Pycolor:
    def __init__(self, **kwargs):
        self.color_mode = kwargs.get('color_mode', 'auto')
        """
        0 - no debug
        1 - print received data
        2 - print written data
        3 - print after each pattern applied
        4 - print line numbers before received data
        """
        self.debug = kwargs.get('debug', 0)
        self.execv = kwargs.get('execv', False)

        self.profloader = ProfileLoader()
        self.current_profile = None

        self.linenum = 0

        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.color_state_orig = ColorState()
        self.color_state = self.color_state_orig.copy()

    @property
    def profiles(self):
        return self.profloader.profiles

    @property
    def profile_default(self):
        return self.profloader.profile_default

    def load_file(self, fname):
        self.profloader.load_file(fname)

    def get_profile_by_name(self, name):
        return self.profloader.get_profile_by_name(name)

    def get_profile_by_command(self, command, args):
        return self.profloader.get_profile_by_command(command, args)

    def execute(self, cmd, profile=None):
        if profile is None:
            profile = self.profloader.get_profile_by_command(cmd[0], cmd[1:])

        self.set_current_profile(profile)
        profile = self.current_profile

        if self.profloader.is_default_profile(profile) and self.debug == 0 and self.execv:
            cmd_path = which(cmd[0])
            if cmd_path is not None:
                cmd_path = cmd_path.decode('utf-8')
            else:
                cmd_path = cmd[0]
            os.execv(cmd_path, cmd)
            sys.exit(0)

        self.debug_print(1, 'using profile "%s"', profile.get_name())

        if profile.less_output:
            tmpfile = tempfile.NamedTemporaryFile()
            self.stdout = io.TextIOWrapper(tmpfile)
            if self.color_mode == 'auto':
                self.color_mode = 'always'

        retcode = execute.execute(
            cmd,
            self.stdout_cb,
            self.stderr_cb,
            tty=profile.tty
        )

        if profile.less_output:
            self.stdout.flush()
            self.stderr.flush()

            pid = os.fork()
            if pid == 0:
                less_path = which('less')
                os.execv(less_path, [less_path, '-FKRSX', tmpfile.name])
                sys.exit(0)
            os.wait()

        return retcode

    def data_callback(self, stream, data):
        color_positions = {}
        removed_newline = False
        removed_carriagereturn = False

        if len(data) != 0 and data[-1] == '\n':
            self.linenum += 1
            data = data[:-1]
            removed_newline = True
        if len(data) != 0 and data[-1] == '\r':
            data = data[:-1]
            removed_carriagereturn = True

        self.debug_print(4, 'on line %d', self.linenum)
        self.debug_print(1, 'received: %s', data.encode('utf-8'))

        color_positions = {}
        context = {
            'color': {
                'enabled': self.is_color_enabled(),
                'aliases': self.profloader.color_aliases,
                'positions': color_positions,
            }
        }

        patcount = 0
        for pat in self.current_profile.patterns:
            if any([
                not pat.enabled,
                pat.stdout_only and stream != self.stdout,
                pat.stderr_only and stream != self.stderr
            ]):
                continue

            matched, applied = apply_pattern(pat, self.linenum, data, context)
            if matched:
                if pat.filter:
                    self.debug_print(2, 'filtered: %s', data.encode('utf-8'))
                    data = None
                    break

                if self.debug >= 3:
                    self.debug_print(3, 'apply%3d: %s',
                        patcount, insert_color_data(applied, color_positions).encode('utf-8')
                    )

                data = applied
                if pat.skip_others:
                    break
            patcount += 1

        if data is None:
            return

        if len(color_positions) != 0:
            data = insert_color_data(data, color_positions)

        self.debug_print(2, 'writing:  %s', data.encode('utf-8'))

        if self.current_profile.timestamp:
            self.write_timestamp(stream)

        stream.flush()
        stream.buffer.write(data.encode('utf-8'))

        self.color_state.set_state_by_string(data)

        if self.current_profile.soft_reset_eol:
            stream.write(self.color_state_orig.get_string(
                compare_state=self.color_state
            ))

        if removed_carriagereturn:
            stream.write('\r')
        if removed_newline:
            stream.write('\n')

        stream.flush()

    def write_timestamp(self, stream):
        timestamp = '%Y-%m-%d %H:%M:%S: '
        if isinstance(self.current_profile.timestamp, str):
            timestamp = self.current_profile.timestamp

        stream.write(self.color_state_orig.get_string(
            compare_state=self.color_state
        ))
        stream.write(datetime.datetime.strftime(datetime.datetime.now(), timestamp))
        stream.write(self.color_state.get_string(
            compare_state=self.color_state_orig
        ))

    def set_current_profile(self, profile):
        if profile is None:
            self.current_profile = self.profloader.profile_default
        else:
            self.current_profile = profile

    def is_color_enabled(self):
        if self.color_mode in ('always', 'on', '1'):
            return True
        if self.color_mode in ('never', 'off', '0'):
            return False
        return not self.is_being_redirected()

    def stdout_cb(self, data):
        self.data_callback(self.stdout, data)

    def stderr_cb(self, data):
        self.data_callback(self.stderr, data)

    def debug_print(self, lvl, val, *args):
        if self.debug < lvl:
            return

        if self.is_color_enabled():
            reset = pyformat.format_string('%Cz%Cde')
            oldstate = str(self.color_state)
            if len(oldstate) == 0:
                oldstate = pyformat.format_string('%Cz')
        else:
            reset = ''
            oldstate = ''

        print('%s    DEBUG%d: %s%s' % (reset, lvl, val % args, oldstate))

    def is_being_redirected(self):
        return not self.stdout.isatty()
