import json
import os
import re
import sys

import execute
from profile_class import Profile
import pyformat
from search_replace import search_replace, update_ranges
from split import re_split
from which import which


class Pycolor:
    def __init__(self, color_mode='auto'):
        self.color_mode = color_mode

        self.profiles = []

        self.current_profile = {}
        self.linenum = 0

    def load_file(self, fname):
        with open(fname, 'r') as file:
            self.parse_file(file)

        for profile in self.profiles:
            self.include_from_profile(
                profile.patterns,
                profile.from_profiles
            )

            for fieldsep in profile.field_separators:
                self.include_from_profile(
                    fieldsep.patterns,
                    fieldsep.from_profiles
                )

    def parse_file(self, file):
        config = json.loads(file.read())

        for prof_cfg in config.get('profiles', []):
            self.profiles.append(Profile(self, prof_cfg))

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
        for profile in self.profiles:
            if profile.profile_name == name:
                return profile
        return None

    def get_profile_by_command(self, command, args):
        for cfg in self.profiles:
            if cfg.which is not None:
                result = which(command)
                if result is not None and result.decode('utf-8') != cfg.which:
                    continue
            if cfg.name is not None and command != cfg.name:
                continue
            if cfg.name_regex is not None and not re.fullmatch(cfg.name_regex, command):
                continue

            if not Pycolor.check_arg_patterns(args, cfg.arg_patterns):
                continue

            return cfg
        return None

    @staticmethod
    def check_arg_patterns(args, arg_patterns):
        for argpat in arg_patterns:
            if 'expression' not in argpat:
                continue

            matches = False
            for idx in Pycolor.get_arg_range(len(args), argpat.get('position')):
                if re.fullmatch(argpat['expression'], args[idx]):
                    if argpat.get('match_not', False):
                        return False
                    matches = True

            if not matches and not argpat.get('optional', False):
                return False

        return True

    @staticmethod
    def get_arg_range(arglen, position):
        if position is None:
            return range(arglen)

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

        if profile is not None:
            self.current_profile = profile
            stdout_cb = self.stdout_cb
            stderr_cb = self.stderr_cb
        else:
            self.current_profile = Profile(self, {
                'profile_name': 'none_found',
                'buffer_line': True
            })
            stdout_cb = Pycolor.stdout_base_cb
            stderr_cb = Pycolor.stderr_base_cb

        if self.current_profile.buffer_line:
            self.linenum = 1
        else:
            self.linenum = 0

        return execute.execute(
            cmd,
            stdout_cb,
            stderr_cb,
            buffer_line=self.current_profile.buffer_line
        )

    def data_callback(self, stream, data):
        newdata = data
        ignore_ranges = []
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

            newdata = self.apply_pattern(pat, newdata, ignore_ranges)

        stream.buffer.write(newdata)

        if removed_newline:
            stream.buffer.write(b'\n')

        stream.flush()

    def apply_pattern(self, pat, data, ignore_ranges):
        sep = pat.separator
        if sep is not None:
            sep = sep.encode('utf-8')

        if not pat.active:
            if pat.activation_regex is None or not re.search(pat.activation_regex, data):
                return data
            pat.active = True

        if pat.deactivation_regex is not None and re.search(pat.deactivation_regex, data):
            pat.active = False
            return data

        if not pat.is_line_active(self.linenum):
            return data

        spl = re_split(sep, data)
        fieldcount = pyformat.fieldsep.idx_to_num(len(spl))

        if pat.min_fields > fieldcount or (
            pat.max_fields > 0 and pat.max_fields < fieldcount
        ):
            return data

        field_idxlist = []
        if pat.field is not None:
            if pat.field == 0:
                field_idxlist = None
            else:
                field_idxlist = [ pyformat.fieldsep.num_to_idx(pat.field) ]
        else:
            field_idxlist = range(0, len(spl), 2)

        if pat.replace_all is not None:
            def match_and_replace(spl, indata):
                match = re.search(pat.regex, indata)
                if match is not None:
                    data = pyformat.format_string(
                        pat.replace_all.decode('utf-8'),
                        context={
                            'fields': spl,
                            'match': match
                        }
                    ).encode('utf-8')

                    spl.clear()
                    spl.extend(re_split(sep, data))
                    ignore_ranges.clear()
                    ignore_ranges.append( (0, len(data)) )

            if field_idxlist is not None:
                for field_idx in field_idxlist:
                    match_and_replace(spl, spl[field_idx])
            else:
                match_and_replace(spl, b''.join(spl))
        elif pat.replace is not None:
            if field_idxlist is not None:
                for field_idx in field_idxlist:
                    newfield, replace_ranges = Pycolor.pat_schrep(
                        pat,
                        spl[field_idx],
                        pat.replace,
                        ignore_ranges
                    )
                    if len(replace_ranges) != 0:
                        spl[field_idx] = newfield

                        offset = 0
                        for i in range(field_idx):
                            offset += len(spl[i])

                        for idx in range(len(replace_ranges)): #pylint: disable=consider-using-enumerate
                            old_range, new_range = replace_ranges[idx]
                            replace_ranges[idx] = (
                                (old_range[0] + offset, old_range[1] + offset),
                                (new_range[0] + offset, new_range[1] + offset),
                            )

                        update_ranges(ignore_ranges, replace_ranges)
            else:
                replaced, replace_ranges = Pycolor.pat_schrep(
                    pat,
                    b''.join(spl),
                    pat.replace,
                    ignore_ranges
                )
                if len(replace_ranges) != 0:
                    update_ranges(ignore_ranges, replace_ranges)
                    spl = re_split(sep, replaced)

        return b''.join(spl)

    @staticmethod
    def pat_schrep(pattern, string, replace, ignore_ranges):
        return search_replace(
            pattern.regex,
            string,
            lambda x: pyformat.format_string(
                replace.decode('utf-8'),
                context={
                    'match': x
                }
            ).encode('utf-8'),
            ignore_ranges=ignore_ranges,
            start_occurrance=pattern.start_occurrance,
            max_count=pattern.max_count
        )

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
        # https://stackoverflow.com/a/1512526
        return os.fstat(0) != os.fstat(1)
