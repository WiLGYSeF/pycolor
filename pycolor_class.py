import datetime
import io
import json
import os
import re
import sys
import tempfile

from colorstate import ColorState
import execute
from profile_class import Profile
import pyformat
from search_replace import search_replace, update_positions
from split import re_split
from which import which


class Pycolor:
    def __init__(self, color_mode='auto', debug=0):
        self.color_mode = color_mode
        self.debug = debug

        self.profiles = []
        self.named_profiles = {}

        self.color_aliases = {}

        self.current_profile = None
        self.profile_default = Profile({
            'profile_name': 'none_found_default',
            'buffer_line': True
        })
        self.linenum = 0

        self.less_process = None

        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.color_state_orig = ColorState()
        self.color_state = self.color_state_orig.copy()

    def load_file(self, fname):
        with open(fname, 'r') as file:
            profiles = self.parse_file(file)

            for prof in profiles:
                self.profiles.append(prof)

                if prof.profile_name is not None:
                    self.named_profiles[prof.profile_name] = prof

            for prof in profiles:
                self.include_from_profile(
                    prof.patterns,
                    prof.from_profiles
                )

    def parse_file(self, file):
        config = json.loads(file.read())
        profiles = []

        self.color_aliases.update(config.get('color_aliases', {}))

        for cfg in config.get('profiles', []):
            profiles.append(Profile(cfg))

        return profiles

    def include_from_profile(self, patterns, from_profiles):
        for fprof in from_profiles:
            if not fprof.enabled:
                continue

            fromprof = self.get_profile_by_name(fprof.name)
            if fprof.order == 'before':
                orig_patterns = patterns.copy()
                patterns.clear()
                patterns.extend(fromprof.patterns)
                patterns.extend(orig_patterns)
            elif fprof.order == 'after':
                patterns.extend(fromprof.patterns)

    def get_profile_by_name(self, name):
        return self.named_profiles.get(name)

    def get_profile_by_command(self, command, args):
        matches = []

        for prof in self.profiles:
            if not any([
                prof.which,
                prof.name,
                prof.name_regex
            ]):
                continue

            if prof.which is not None:
                result = which(command)
                if result is not None and result.decode('utf-8') != prof.which:
                    continue
            if prof.name is not None and command != prof.name:
                continue
            if prof.name_regex is not None and not re.fullmatch(prof.name_regex, command):
                continue

            if not Pycolor.check_arg_patterns(args, prof.arg_patterns, prof.all_args_must_match):
                continue

            matches.append(prof)

        if len(matches) == 0:
            return None
        return matches[-1]

    @staticmethod
    def check_arg_patterns(args, arg_patterns, all_must_match=False):
        idx_matches = set()

        for argpat in arg_patterns:
            matches = False
            for idx in argpat.get_arg_range(len(args)):
                if argpat.regex.fullmatch(args[idx]):
                    if argpat.match_not:
                        return False
                    idx_matches.add(idx)
                    matches = True

            if not any([
                matches,
                argpat.match_not,
                argpat.optional
            ]):
                return False

        if all_must_match and len(idx_matches) != len(args):
            return False

        return True

    def execute(self, cmd, profile=None):
        if profile is None:
            profile = self.get_profile_by_command(cmd[0], cmd[1:])

        self.set_current_profile(profile)
        profile = self.current_profile

        if self.debug > 0:
            name = None
            for pname in [
                profile.profile_name,
                profile.which,
                profile.name,
                profile.name_regex,
            ]:
                if pname is not None and len(pname) != 0:
                    name = pname
                    break

            self.debug_print(1, 'using profile "%s"' % name)

        if profile.less_output:
            tmpfile = tempfile.NamedTemporaryFile()
            self.stdout = io.TextIOWrapper(tmpfile)

        retcode = execute.execute(
            cmd,
            self.stdout_cb,
            self.stderr_cb,
            buffer_line=self.current_profile.buffer_line
        )

        if profile.less_output:
            pid = os.fork()
            if pid == 0:
                os.execv(which('less'), ['-FKRSX', tmpfile.name])
                sys.exit(0)
        return retcode

    def data_callback(self, stream, data):
        newdata = data
        color_positions = {}
        removed_newline = False

        if self.current_profile.buffer_line:
            if newdata[-1] == '\n':
                self.linenum += 1
                newdata = newdata[:-1]
                removed_newline = True

            self.debug_print(1, 'got data: ln %d: %s' % (self.linenum, newdata.encode('utf-8')))
        else:
            self.linenum += data.count('\n')

            self.debug_print(1, 'got data: %s' % newdata.encode('utf-8'))

        color_pos_len = len(color_positions)
        for pat in self.current_profile.patterns:
            if not pat.enabled:
                continue
            if pat.stdout_only and stream != sys.stdout or pat.stderr_only and stream != sys.stderr:
                continue

            applied = self.apply_pattern(pat, newdata, color_positions)
            if applied is None:
                newdata = None
                break

            if newdata != applied or len(color_positions) > color_pos_len:
                if self.debug >= 3:
                    changed = Pycolor.insert_color_data(applied, color_positions)
                    self.debug_print(3, 'applying: %s' % (changed.encode('utf-8')))

                newdata = applied
                color_pos_len = len(color_positions)

        if newdata is not None:
            if len(color_positions) != 0:
                newdata = Pycolor.insert_color_data(newdata, color_positions)

            self.debug_print(2, 'writing:  %s' % (newdata.encode('utf-8')))

            if self.current_profile.buffer_line:
                if self.current_profile.timestamp != False: #pylint: disable=singleton-comparison
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

            stream.flush()
            # TODO: should we handle unicode differently?
            stream.buffer.write(newdata.encode('utf-8'))

            self.color_state.set_state_by_string(newdata)

            if self.current_profile.buffer_line:
                if self.current_profile.soft_reset_eol:
                    stream.write(self.color_state_orig.get_string(
                        compare_state=self.color_state
                    ))

                if removed_newline:
                    stream.write('\n')

            stream.flush()

    def apply_pattern(self, pat, data, color_positions):
        if not pat.is_active(self.linenum, data):
            return data

        if pat.separator is None:
            if pat.replace is not None:
                data, replace_ranges, colorpos = self.pat_schrep(pat, data)
                update_positions(color_positions, replace_ranges)
                Pycolor.update_color_positions(color_positions, colorpos)
            elif pat.replace_all is not None:
                match = pat.regex.search(data)
                if match is not None:
                    data, colorpos = pyformat.format_string(
                        pat.replace_all,
                        context={
                            'color_state_orig': self.color_state_orig,
                            'color_state': self.color_state,
                            'color_enabled': self.is_color_enabled(),
                            'color_aliases': self.color_aliases,
                            'match': match
                        },
                        return_color_positions=True
                    )
                    color_positions.clear()
                    color_positions.update(colorpos)
            elif pat.filter and pat.regex.search(data):
                return None
            return data

        fields = re_split(pat.separator, data)
        field_idxs = pat.get_field_indexes(fields)

        if pat.replace_all is not None:
            for field_idx in field_idxs:
                match = pat.regex.search(fields[field_idx])
                if match is None:
                    continue

                data, colorpos = pyformat.format_string(
                    pat.replace_all,
                    context={
                        'color_state_orig': self.color_state_orig,
                        'color_state': self.color_state,
                        'color_enabled': self.is_color_enabled(),
                        'color_aliases': self.color_aliases,
                        'fields': fields,
                        'match': match
                    },
                    return_color_positions=True
                )

                color_positions.clear()
                color_positions.update(colorpos)
                return data

        if pat.replace is not None:
            for field_idx in field_idxs:
                newfield, replace_ranges, colorpos = self.pat_schrep(pat, fields[field_idx])
                fields[field_idx] = newfield

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
            return ''.join(fields)

        if pat.filter:
            for field_idx in field_idxs:
                match = pat.regex.search(fields[field_idx])
                if match is not None:
                    return None

        return data

    def pat_schrep(self, pattern, string):
        color_positions = {}

        def replacer(match):
            newstring, colorpos = pyformat.format_string(
                pattern.replace,
                context={
                    'color_state_orig': self.color_state_orig,
                    'color_state': self.color_state,
                    'color_enabled': self.is_color_enabled(),
                    'color_aliases': self.color_aliases,
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

    def set_current_profile(self, profile):
        if profile is None:
            self.current_profile = self.profile_default
        else:
            self.current_profile = profile

        self.linenum = 0

    def is_color_enabled(self):
        if self.color_mode in ('always', 'on', '1'):
            return True
        if self.color_mode in ('never', 'off', '0'):
            return False
        return not Pycolor.is_being_redirected()

    def stdout_cb(self, data):
        self.data_callback(self.stdout, data)

    def stderr_cb(self, data):
        self.data_callback(self.stderr, data)

    def debug_print(self, lvl, *args):
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

        print('%s    DEBUG%d: %s%s' % (reset, lvl, ' '.join(args), oldstate))

    @staticmethod
    def is_being_redirected():
        return not sys.stdout.isatty()
