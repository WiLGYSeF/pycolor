import datetime
import io
import os
import sys
import tempfile

from colorstate import ColorState
import execute
import pyformat
from profileloader import ProfileLoader
from search_replace import search_replace, update_positions
from split import re_split
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

    def execute(self, cmd, profile=None):
        if profile is None:
            profile = self.profloader.get_profile_by_command(cmd[0], cmd[1:])

        self.set_current_profile(profile)
        profile = self.current_profile

        if self.profloader.is_default_profile(profile) and self.debug == 0 and self.execv:
            cmd_path = which(cmd[0])
            os.execv(cmd_path.decode('utf-8'), cmd)
            sys.exit(0)

        self.debug_print(1, 'using profile "%s"', profile.get_name())

        if profile.less_output:
            tmpfile = tempfile.NamedTemporaryFile()
            self.stdout = io.TextIOWrapper(tmpfile)

        retcode = execute.execute(
            cmd,
            self.stdout_cb,
            self.stderr_cb,
            buffer_line=profile.buffer_line,
            tty=profile.tty
        )

        if profile.less_output:
            self.stdout.flush()
            self.stderr.flush()

            if isinstance(profile.less_output, str):
                less_path = profile.less_output
            else:
                less_path = which('less')

            # TODO: does not delete tempfile
            os.execv(less_path, [less_path, '-FKRSX', tmpfile.name])
            sys.exit(0)
        return retcode

    def data_callback(self, stream, data):
        newdata = data
        color_positions = {}
        removed_newline = False
        removed_carriagereturn = False

        if self.current_profile.buffer_line:
            if len(newdata) != 0 and newdata[-1] == '\n':
                self.linenum += 1
                newdata = newdata[:-1]
                removed_newline = True
            if len(newdata) != 0 and newdata[-1] == '\r':
                newdata = newdata[:-1]
                removed_carriagereturn = True

            self.debug_print(4, 'on line %d', self.linenum)
        else:
            self.linenum += data.count('\n')

        self.debug_print(1, 'received: %s', newdata.encode('utf-8'))

        for pat in self.current_profile.patterns:
            if any((
                not pat.enabled,
                pat.stdout_only and stream != self.stdout,
                pat.stderr_only and stream != self.stderr
            )):
                continue

            matched, applied = self.apply_pattern(pat, newdata, color_positions)
            if matched:
                if pat.filter:
                    self.debug_print(2, 'filtered: %s', newdata.encode('utf-8'))
                    newdata = None
                    break

                if self.debug >= 3:
                    self.debug_print(3, 'applying: %s',
                        Pycolor.insert_color_data(applied, color_positions).encode('utf-8')
                    )

                newdata = applied
                if pat.skip_others:
                    break

        if newdata is None:
            return

        if len(color_positions) != 0:
            newdata = Pycolor.insert_color_data(newdata, color_positions)

        self.debug_print(2, 'writing:  %s', newdata.encode('utf-8'))

        if self.current_profile.buffer_line and self.current_profile.timestamp:
            self.write_timestamp(stream)

        stream.flush()
        stream.buffer.write(newdata.encode('utf-8'))

        self.color_state.set_state_by_string(newdata)

        if self.current_profile.buffer_line:
            if self.current_profile.soft_reset_eol:
                stream.write(self.color_state_orig.get_string(
                    compare_state=self.color_state
                ))

            if removed_carriagereturn:
                stream.write('\r')
            if removed_newline:
                stream.write('\n')

        stream.flush()

    def apply_pattern(self, pat, data, color_positions):
        if not pat.is_active(self.linenum, data):
            return False, None
        if pat.super_regex is not None and not pat.super_regex.search(data):
            return False, None

        context = {
            'color_state_orig': self.color_state_orig,
            'color_state': self.color_state,
            'color_enabled': self.is_color_enabled(),
            'color_aliases': self.profloader.color_aliases,
        }

        if pat.separator_regex is not None:
            fields = re_split(pat.separator_regex, data)
            field_idxs = pat.get_field_indexes(fields)
            context['fields'] = fields

        if pat.separator_regex is None or (pat.field is not None and pat.field < 0):
            if pat.replace_all is not None:
                match = pat.regex.search(data)
                if match is None:
                    return False, None

                context['match'] = match

                data, colorpos = pyformat.format_string(
                    pat.replace_all,
                    context=context,
                    return_color_positions=True
                )
                color_positions.clear()
                color_positions.update(colorpos)
                return True, data
            if pat.replace is not None:
                data, replace_ranges, colorpos = self.pat_schrep(pat, data)
                if len(replace_ranges) == 0:
                    return False, None

                update_positions(color_positions, replace_ranges)
                Pycolor.update_color_positions(color_positions, colorpos)
                return True, data
            if len(pat.replace_groups) != 0:
                match = pat.regex.search(data)
                if match is not None:
                    context['match'] = match

                    last = match.start(0)
                    new_match_data = data[:last]
                    choffset = 0
                    replace_ranges = []

                    groupdict = match.groupdict()
                    group_idx_to_name = {}

                    for i in range(1, len(match.groups()) + 1):
                        span = match.span(i)
                        for group in groupdict:
                            if match.span(group) == span:
                                group_idx_to_name[i] = group
                                break

                    for i in range(1, len(match.groups()) + 1):
                        new_match_data += data[last:match.start(i)]
                        replace_val = None
                        if isinstance(pat.replace_groups, dict):
                            replace_val = pat.replace_groups.get(str(i))
                            if replace_val is None and i in group_idx_to_name:
                                replace_val = pat.replace_groups.get(group_idx_to_name[i])
                        elif isinstance(pat.replace_groups, list) and i <= len(pat.replace_groups):
                            replace_val = pat.replace_groups[i - 1]

                        if replace_val is not None:
                            context['match_curr'] = match.group(i)
                            format_data, colorpos = pyformat.format_string(
                                replace_val,
                                context=context,
                                return_color_positions=True
                            )
                            new_match_data += format_data

                            colorpos = Pycolor.offset_color_positions(colorpos, match.start(i))
                            choffset += len(format_data) - (match.end(i) - match.start(i))
                            update_positions(colorpos, replace_ranges)
                            replace_ranges.append((
                                match.span(i),
                                (
                                    match.start(i) + choffset,
                                    match.start(i) + choffset + len(format_data)
                                )
                            ))
                            Pycolor.update_color_positions(color_positions, colorpos)
                        else:
                            new_match_data += match.group(i)
                        last = match.end(i)

                    new_match_data += data[match.end(0):]
                    return True, new_match_data
                return False, None
            return pat.regex.search(data), data

        if pat.replace_all is not None:
            for field_idx in field_idxs:
                match = pat.regex.search(fields[field_idx])
                if match is None:
                    continue

                context['match'] = match

                data, colorpos = pyformat.format_string(
                    pat.replace_all,
                    context=context,
                    return_color_positions=True
                )

                color_positions.clear()
                color_positions.update(colorpos)
                return True, data

        if pat.replace is not None:
            matched = False
            for field_idx in field_idxs:
                newfield, replace_ranges, colorpos = self.pat_schrep(pat, fields[field_idx])
                if len(replace_ranges) == 0:
                    continue
                fields[field_idx] = newfield
                matched = True

                offset = 0
                for i in range(field_idx):
                    offset += len(fields[i])

                for idx in range(len(replace_ranges)): #pylint: disable=consider-using-enumerate
                    old_range, new_range = replace_ranges[idx]
                    replace_ranges[idx] = (
                        (old_range[0] + offset, old_range[1] + offset),
                        (new_range[0] + offset, new_range[1] + offset),
                    )

                if offset > 0:
                    for key in sorted(colorpos.keys(), reverse=True):
                        colorpos[key + offset] = colorpos[key]
                        del colorpos[key]

                update_positions(color_positions, replace_ranges)
                Pycolor.update_color_positions(color_positions, colorpos)
            if not matched:
                return False, None
            return True, ''.join(fields)

        for field_idx in field_idxs:
            match = pat.regex.search(fields[field_idx])
            if match is not None:
                return True, data

        return False, None

    def pat_schrep(self, pattern, string):
        color_positions = {}

        def replacer(match):
            newstring, colorpos = pyformat.format_string(
                pattern.replace,
                context={
                    'color_state_orig': self.color_state_orig,
                    'color_state': self.color_state,
                    'color_enabled': self.is_color_enabled(),
                    'color_aliases': self.profloader.color_aliases,
                    'match': match
                },
                return_color_positions=True
            )

            if match.start() > 0:
                for key in sorted(colorpos.keys(), reverse=True):
                    newkey = key + match.start()
                    colorpos[newkey] = colorpos[key]
                    del colorpos[key]

            color_positions.update(colorpos)
            return newstring

        newstring, replace_ranges = search_replace(
            pattern.regex,
            string,
            replacer,
            ignore_ranges=[],
            start_occurrence=pattern.start_occurrence,
            max_count=pattern.max_count
        )
        return newstring, replace_ranges, color_positions

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

    @staticmethod
    def insert_color_data(data, color_positions):
        colored_data = ''
        last = 0

        for key in sorted(color_positions.keys()):
            colored_data += data[last:key] + color_positions[key]
            last = key

        return colored_data + data[last:]

    @staticmethod
    def update_color_positions(color_positions, pos):
        if len(pos) == 0:
            return

        keys_pos = sorted(pos.keys())
        keys_col = set(color_positions.keys())

        for idx in range(0, len(keys_pos) - 1, 2):
            first = keys_pos[idx]
            second = keys_pos[idx + 1]

            to_remove = []
            for key in keys_col:
                if key >= first and key <= second:
                    to_remove.append(key)
                    del color_positions[key]
            for key in to_remove:
                keys_col.remove(key)

            color_positions[first] = pos[first]
            color_positions[second] = pos[second]

            if pyformat.color.is_ansi_reset(pos[second]):
                last = -1
                for key in keys_col:
                    if key < first and key > last:
                        last = key

                if last != -1:
                    color_positions[second] = pos[second] + color_positions[last]

        if (len(pos) & 1) == 1:
            last = keys_pos[-1]
            color_positions[last] = pos[last]

            for key in keys_col:
                if key > last:
                    del color_positions[key]

    @staticmethod
    def offset_color_positions(color_positions, offset):
        newpos = {}
        for key, val in color_positions.items():
            newpos[key + offset] = val
        return newpos

    def set_current_profile(self, profile):
        if profile is None:
            self.current_profile = self.profloader.profile_default
        else:
            self.current_profile = profile

        self.linenum = 0

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
