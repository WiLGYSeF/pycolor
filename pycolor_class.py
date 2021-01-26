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
            for idx in Pycolor.get_arg_range(len(args), argpat.get('position')):
                if argpat['regex'].fullmatch(args[idx]):
                    if argpat.get('match_not', False):
                        return False
                    idx_matches.add(idx)
                    matches = True

            if not any([
                matches,
                argpat.get('match_not', False),
                argpat.get('optional', False)
            ]):
                return False

        if all_must_match and len(idx_matches) != len(args):
            return False

        return True

    @staticmethod
    def get_arg_range(arglen, position):
        if position is None:
            return range(arglen)

        if isinstance(position, int):
            if position > arglen:
                return range(0)
            return range(position - 1, position)

        match = re.fullmatch(r'([<>+-])?(\*|[0-9]+)', position)
        if match is None:
            return range(arglen)

        index = match[2]
        if index == '*':
            return range(arglen)
        index = int(index)

        arg_range = None
        modifier = match[1]

        if modifier is None:
            arg_range = range(index - 1, min(index, arglen))
        elif modifier in ('>', '+'):
            arg_range = range(index - 1, arglen)
        elif modifier in ('<', '-'):
            arg_range = range(0, min(index, arglen))
        return arg_range

    def execute(self, cmd, profile=None):
        if profile is None:
            profile = self.get_profile_by_command(cmd[0], cmd[1:])

        self.set_current_profile(profile)

        if profile is not None:
            stdout_cb = self.stdout_cb
            stderr_cb = self.stderr_cb
        else:
            stdout_cb = Pycolor.stdout_base_cb
            stderr_cb = Pycolor.stderr_base_cb

        return execute.execute(
            cmd,
            stdout_cb,
            stderr_cb,
            buffer_line=self.current_profile.buffer_line
        )

    def data_callback(self, stream, data):
        newdata = data
        color_positions = {}
        removed_newline = False

        if self.current_profile.buffer_line:
            self.linenum += 1

            if newdata[-1] == ord('\n'):
                newdata = newdata[:-1]
                removed_newline = True
        else:
            self.linenum += data.count(b'\n')

        for pat in self.current_profile.patterns:
            if not pat.enabled:
                continue
            if pat.stdout_only and stream != sys.stdout or pat.stderr_only and stream != sys.stderr:
                continue

            newdata = self.apply_pattern(pat, newdata, color_positions)
            if newdata is None:
                break

        if len(color_positions) > 0:
            newdata = Pycolor.insert_color_data(newdata, color_positions)

        if newdata is not None:
            stream.buffer.write(newdata)
            if removed_newline:
                stream.buffer.write(b'\n')

            stream.flush()

    def apply_pattern(self, pat, data, color_positions):
        if not pat.active:
            if pat.activation_regex is None or not re.search(pat.activation_regex, data):
                return data
            pat.active = True

        if pat.deactivation_regex is not None and re.search(pat.deactivation_regex, data):
            pat.active = False
            return data

        if not pat.is_line_active(self.linenum):
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
                        pat.replace_all.decode('utf-8'),
                        context={
                            'color_enabled': self.is_color_enabled(),
                            'color_aliases': self.color_aliases,
                            'match': match
                        },
                        return_color_positions=True
                    )
                    data = data.encode('utf-8')
                    color_positions.clear()
                    color_positions.update(colorpos)
            elif pat.filter and pat.regex.search(data):
                return None
            return data

        fields = re_split(pat.separator.encode('utf-8'), data)
        fieldcount = pyformat.fieldsep.idx_to_num(len(fields))

        if pat.min_fields > fieldcount or (
            pat.max_fields > 0 and pat.max_fields < fieldcount
        ):
            return data

        field_idxlist = []
        if pat.field is not None and pat.field > 0:
            if pat.field > fieldcount:
                return data
            field_idxlist = [ pyformat.fieldsep.num_to_idx(pat.field) ]
        else:
            field_idxlist = range(0, len(fields), 2)

        if pat.replace_all is not None:
            for field_idx in field_idxlist:
                match = pat.regex.search(fields[field_idx])
                if match is None:
                    continue

                data, colorpos = pyformat.format_string(
                    pat.replace_all.decode('utf-8'),
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
                return data.encode('utf-8')

        if pat.replace is not None:
            for field_idx in field_idxlist:
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
            return b''.join(fields)

        if pat.filter:
            for field_idx in field_idxlist:
                match = pat.regex.search(fields[field_idx])
                if match is not None:
                    return None

        return data

    def pat_schrep(self, pattern, string):
        color_positions = {}

        def replacer(match):
            newstring, colorpos = pyformat.format_string(
                pattern.replace.decode('utf-8'),
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
            return newstring.encode('utf-8')

        newstring, replace_ranges = search_replace(
            pattern.regex,
            string,
            replacer,
            ignore_ranges=[],
            start_occurrance=pattern.start_occurrance,
            max_count=pattern.max_count
        )
        return newstring, replace_ranges, color_positions

    @staticmethod
    def insert_color_data(data, color_positions):
        colored_data = b''
        last = 0

        for key in sorted(color_positions.keys()):
            colored_data += data[last:key] + color_positions[key].encode('utf-8')
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
        if self.color_mode == 'on':
            return True
        if self.color_mode == 'off':
            return False
        return not Pycolor.is_being_redirected()

    def stdout_cb(self, data):
        self.data_callback(sys.stdout, data)

    def stderr_cb(self, data):
        self.data_callback(sys.stderr, data)

    @staticmethod
    def stdout_base_cb(data):
        sys.stdout.buffer.write(data)
        sys.stdout.flush()

    @staticmethod
    def stderr_base_cb(data):
        sys.stderr.buffer.write(data)
        sys.stderr.flush()

    @staticmethod
    def is_being_redirected():
        return not sys.stdout.isatty()
