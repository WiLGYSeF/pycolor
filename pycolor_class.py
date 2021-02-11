import json
import re
import sys

import execute
from profile_class import Profile
import pyformat
from search_replace import search_replace, update_positions
from split import re_split
from which import which


class Pycolor:
    def __init__(self, color_mode='auto'):
        self.color_mode = color_mode

        self.profiles = []
        self.named_profiles = {}

        self.color_aliases = {}

        self.current_profile = None
        self.linenum = 0

        self.stdout = sys.stdout
        self.stderr = sys.stderr

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
        if isinstance(from_profiles, str):
            fromprof = self.get_profile_by_name(from_profiles)
            if fromprof is None:
                raise Exception()

            patterns.extend(fromprof.patterns)
            return

        for fromprof_cfg in from_profiles:
            if isinstance(fromprof_cfg, dict):
                if not fromprof_cfg.get('enabled', True):
                    continue

                if len(fromprof_cfg.get('name', '')) == 0:
                    raise Exception()

                fromprof = self.get_profile_by_name(fromprof_cfg['name'])
                if fromprof is None:
                    raise Exception()

                if 'order' in fromprof_cfg:
                    if fromprof_cfg['order'] not in ('before', 'after', 'disabled'):
                        raise ValueError()

                    if fromprof_cfg['order'] == 'before':
                        orig_patterns = patterns.copy()
                        patterns.clear()
                        patterns.extend(fromprof.patterns)
                        patterns.extend(orig_patterns)
                    elif fromprof_cfg['order'] == 'after':
                        patterns.extend(fromprof.patterns)
                else:
                    patterns.extend(fromprof.patterns)
            elif isinstance(fromprof_cfg, str):
                fromprof = self.get_profile_by_name(fromprof_cfg)
                if fromprof is None:
                    raise Exception()

                patterns.extend(fromprof.patterns)
            else:
                raise ValueError()

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

        return execute.execute(
            cmd,
            self.stdout_cb,
            self.stderr_cb,
            buffer_line=self.current_profile.buffer_line
        )

    def data_callback(self, stream, data):
        newdata = data
        color_positions = {}
        removed_newline = False

        if self.current_profile.buffer_line:
            if newdata[-1] == '\n':
                self.linenum += 1
                newdata = newdata[:-1]
                removed_newline = True
        else:
            self.linenum += data.count('\n')

        for pat in self.current_profile.patterns:
            if not pat.enabled:
                continue
            if pat.stdout_only and stream != sys.stdout or pat.stderr_only and stream != sys.stderr:
                continue

            newdata = self.apply_pattern(pat, newdata, color_positions)
            if newdata is None:
                break

        if newdata is not None:
            if len(color_positions) > 0:
                newdata = Pycolor.insert_color_data(newdata, color_positions)

            stream.write(newdata)
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
            self.current_profile = Profile({
                'profile_name': 'none_found',
                'buffer_line': True
            })
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

    @staticmethod
    def is_being_redirected():
        return not sys.stdout.isatty()
