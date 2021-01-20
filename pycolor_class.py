import json
import os
import re
import sys

import execute
from pattern import Pattern
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
                profile['patterns'],
                profile['from_profiles']
            )

            for fieldsep in profile['field_separators']:
                self.include_from_profile(
                    fieldsep['patterns'],
                    fieldsep['from_profiles']
                )

    def parse_file(self, file):
        config = json.loads(file.read())

        def init_pattern(cfg):
            pattern = Pattern(cfg)

            if 'replace' in cfg:
                pattern.replace = pyformat.format_string(
                    cfg['replace'],
                    context={
                        'color_enabled': self.is_color_enabled()
                    }
                ).encode('utf-8')

            if 'replace_all' in cfg:
                pattern.replace_all = pyformat.format_string(
                    cfg['replace_all'],
                    context={
                        'color_enabled': self.is_color_enabled()
                    }
                ).encode('utf-8')

            return pattern

        for prof_cfg in config.get('profiles', []):
            profile = {
                'name': prof_cfg.get('name'),
                'profile_name': prof_cfg.get('profile_name'),
                'which': prof_cfg.get('which'),
                'arg_patterns': prof_cfg.get('arg_patterns'),
                'buffer_line': prof_cfg.get('buffer_line', True),
                'from_profiles': prof_cfg.get('from_profiles', []),
                'patterns': [],
                'field_separators': []
            }

            for pattern_cfg in prof_cfg.get('patterns', []):
                profile['patterns'].append(init_pattern(pattern_cfg))

            self.profiles.append(profile)

    def include_from_profile(self, patterns, from_profiles):
        if isinstance(from_profiles, str):
            fromprof = self.get_profile_by_name(from_profiles)
            if fromprof is None:
                raise Exception()

            patterns.extend(fromprof['patterns'])
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
                        raise Exception()

                    if fromprof_cfg['order'] == 'before':
                        orig_patterns = patterns.copy()
                        patterns.clear()
                        patterns.extend(fromprof['patterns'])
                        patterns.extend(orig_patterns)
                    elif fromprof_cfg['order'] == 'after':
                        patterns.extend(fromprof['patterns'])
                else:
                    patterns.extend(fromprof['patterns'])
            elif isinstance(fromprof_cfg, str):
                fromprof = self.get_profile_by_name(fromprof_cfg)
                if fromprof is None:
                    raise Exception()

                patterns.extend(fromprof['patterns'])
            else:
                raise Exception()

    def get_profile_by_name(self, name):
        for profile in self.profiles:
            if profile.get('profile_name') == name:
                return profile
        return None

    def get_profile_by_command(self, command, args):
        for cfg in self.profiles:
            result = which(command)
            if result is not None and result.decode('utf-8') != cfg['which']:
                continue
            if command != cfg['name']:
                continue

            skip_profile = False

            for arg_pat in cfg.get('arg_patterns', []):
                if skip_profile:
                    break
                if 'expression' not in arg_pat:
                    continue

                if 'position' in arg_pat:
                    match = re.fullmatch(r'([<>+-])?([*0-9]+)', arg_pat['position'])
                    if match is not None:
                        modifier = match[1]
                        index = match[2]

                        if index != '*':
                            index = int(index)
                            if modifier is None:
                                check_arg_range = range(index - 1, min(index, len(args)))
                            elif modifier == '>' or modifier == '+':
                                check_arg_range = range(index - 1, len(args))
                            elif modifier == '<' or modifier == '-':
                                check_arg_range = range(0, min(index, len(args)))
                        else:
                            check_arg_range = range(len(args))
                    else:
                        check_arg_range = range(len(args))
                else:
                    check_arg_range = range(len(args))

                match = False

                for idx in check_arg_range:
                    arg = args[idx]
                    print(arg_pat['expression'], arg)

                    if re.fullmatch(arg_pat['expression'], arg):
                        match = True
                        if arg_pat.get('match_not', False):
                            skip_profile = True
                            break

                if not match and not arg_pat.get('optional', False):
                    skip_profile = True

            if skip_profile:
                continue

            return cfg
        return None

    def execute(self, cmd, profile=None):
        if profile is None:
            profile = self.get_profile_by_command(cmd[0], cmd[1:])

        if profile is not None:
            self.current_profile = profile
            stdout_cb = self.stdout_cb
            stderr_cb = self.stderr_cb
        else:
            self.current_profile = {
                'buffer_line': True
            }
            stdout_cb = Pycolor.stdout_base_cb
            stderr_cb = Pycolor.stderr_base_cb

        if self.current_profile['buffer_line']:
            self.linenum = 1
        else:
            self.linenum = 0

        return execute.execute(
            cmd,
            stdout_cb,
            stderr_cb,
            buffer_line=self.current_profile['buffer_line']
        )

    def data_callback(self, stream, data):
        newdata = data
        ignore_ranges = []
        removed_newline = False

        if self.current_profile['buffer_line']:
            self.linenum += 1

            if newdata[-1] == ord('\n'):
                newdata = newdata[:-1]
                removed_newline = True
        else:
            self.linenum += data.count(b'\n')

        def pat_schrep(pattern, string, replace):
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

        for pat in self.current_profile['patterns']:
            if not pat.enabled:
                continue

            sep = pat.separator
            if sep is not None:
                sep = sep.encode('utf-8')

            if not pat.active:
                if pat.activation_regex is not None and re.search(pat.activation_regex, data):
                    pat.active = True
                else:
                    continue

            if pat.deactivation_regex is not None and re.search(pat.deactivation_regex, data):
                pat.active = False
                continue

            if not pat.is_line_active(self.linenum):
                continue

            spl = re_split(sep, newdata)
            fieldcount = pyformat.fieldsep.idx_to_num(len(spl))

            if pat.min_fields > fieldcount or (
                pat.max_fields > 0 and pat.max_fields < fieldcount
            ):
                continue

            field_idxlist = []
            if pat.field is not None:
                if pat.field == 0:
                    field_idxlist = None
                else:
                    field_idxlist = [ pyformat.fieldsep.num_to_idx(pat.field) ]
            else:
                field_idxlist = range(0, len(spl), 2)

            if pat.replace_all is not None:
                if field_idxlist is not None:
                    for field_idx in field_idxlist:
                        match = re.search(pat.regex, spl[field_idx])
                        if match is not None:
                            newdata = pyformat.format_string(
                                pat.replace_all.decode('utf-8'),
                                context={
                                    'fields': spl,
                                    'match': match
                                }
                            ).encode('utf-8')

                            spl = re_split(sep, newdata)
                            ignore_ranges = [(0, len(newdata))]
                else:
                    match = re.search(pat.regex, b''.join(spl))
                    if match is not None:
                        newdata = pyformat.format_string(
                            pat.replace_all.decode('utf-8'),
                            context={
                                'fields': spl,
                                'match': match
                            }
                        ).encode('utf-8')

                        spl = re_split(sep, newdata)
                        ignore_ranges = [(0, len(newdata))]
            elif pat.replace is not None:
                if field_idxlist is not None:
                    for field_idx in field_idxlist:
                        newfield, replace_ranges = pat_schrep(
                            pat,
                            spl[field_idx],
                            pat.replace
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
                    replaced, replace_ranges = pat_schrep(
                        pat,
                        b''.join(spl),
                        pat.replace
                    )
                    if len(replace_ranges) != 0:
                        update_ranges(ignore_ranges, replace_ranges)
                        spl = re_split(sep, replaced)
                        newdata = b''.join(spl)

            newdata = b''.join(spl)

        stream.buffer.write(newdata)

        if removed_newline:
            stream.buffer.write(b'\n')

        stream.flush()

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
