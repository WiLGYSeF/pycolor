#!/usr/bin/env python3

import json
import os
import re
import sys

import execute
import pyformat
from search_replace import search_replace, update_ranges
from split import re_split
from which import which


PYCOLOR_CONFIG_FNAME = 'config.json'


class Pycolor:
    def __init__(self):
        self.profiles = []

        with open(PYCOLOR_CONFIG_FNAME, 'r') as file:
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

        self.current_profile = {}
        self.linecount = 0

    def parse_file(self, file):
        config = json.loads(file.read())

        def init_pattern(cfg):
            if 'expression' not in cfg:
                raise Exception()

            pattern = {
                'field': cfg.get('field'),
                'min_fields': cfg.get('min_fields', -1),
                'max_fields': cfg.get('max_fields', -1),
                'expression': cfg['expression'],
                'regex': re.compile(cfg['expression'].encode('utf-8')),
                'filter': cfg.get('filter', False),
                'start_occurrance': cfg.get('start_occurrance', 1),
                'max_count': cfg.get('max_count', -1),
                'activation_line': cfg.get('activation_line', -1),
                'deactivation_line': cfg.get('deactivation_line', -1),
                'activation_expression': cfg.get('activation_expression'),
                'deactivation_expression': cfg.get('deactivation_expression'),
            }

            if 'replace' in cfg:
                pattern['replace'] = pyformat.format_string(
                    cfg['replace'],
                    context={
                        'color_enabled': not is_being_redirected()
                    }
                ).encode('utf-8')

            return pattern

        for prof_cfg in config.get('profiles', []):
            profile = {
                'name': prof_cfg.get('name'),
                'profile_name': prof_cfg.get('profile_name'),
                'which': prof_cfg.get('which'),
                'buffer_line': prof_cfg.get('buffer_line', True),
                'from_profiles': prof_cfg.get('from_profiles', []),
                'patterns': [],
                'field_separators': []
            }

            for pattern_cfg in prof_cfg.get('patterns', []):
                profile['patterns'].append(init_pattern(pattern_cfg))

            for fieldsep_cfg in prof_cfg.get('field_separators', []):
                if 'separator' not in fieldsep_cfg:
                    raise Exception()

                fieldsep = {
                    'separator': fieldsep_cfg['separator'],
                    'from_profiles': fieldsep_cfg.get('from_profiles', []),
                    'patterns': []
                }

                for pattern_cfg in fieldsep_cfg.get('patterns', []):
                    pattern = init_pattern(pattern_cfg)

                    if 'replace_all' in pattern_cfg:
                        pattern['replace_all'] = pyformat.format_string(
                            pattern_cfg['replace_all'],
                            context={
                                'color_enabled': not is_being_redirected()
                            }
                        ).encode('utf-8')
                    fieldsep['patterns'].append(pattern)

                profile['field_separators'].append(fieldsep)

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

    def get_profile_by_command(self, command):
        for cfg in self.profiles:
            result = which(command)
            if result is not None and result.decode('utf-8') == cfg['which']:
                return cfg
            if command == cfg['name']:
                return cfg
        return None

    def execute(self, cmd):
        profile = self.get_profile_by_command(cmd[0])

        if profile is not None:
            self.current_profile = profile
            stdout_cb = self.stdout_cb
            stderr_cb = self.stderr_cb
        else:
            self.current_profile = {}
            stdout_cb = Pycolor.stdout_base_cb
            stderr_cb = Pycolor.stderr_base_cb

        self.linecount = 0

        return execute.execute(
            cmd,
            stdout_cb,
            stderr_cb,
            buffer_line=self.current_profile['buffer_line']
        )

    def data_callback(self, stream, data):
        newdata = data
        ignore_ranges = []

        if self.current_profile['buffer_line']:
            self.linecount += 1
        else:
            self.linecount += data.count(b'\n')

        def pat_schrep(pattern, string, replace):
            return search_replace(
                pattern['regex'],
                string,
                lambda x: pyformat.format_string(
                    replace.decode('utf-8'),
                    context={
                        'match': x
                    }
                ).encode('utf-8'),
                ignore_ranges=ignore_ranges,
                start_occurrance=pattern['start_occurrance'],
                max_count=pattern['max_count']
            )

        for fieldsep in self.current_profile['field_separators']:
            sep = fieldsep['separator']
            spl = re_split(sep.encode('utf-8'), newdata)
            field_idx_set = set()

            for pattern in fieldsep['patterns']:
                fieldcount = pyformat.fieldsep.idx_to_num(len(spl))
                if pattern['min_fields'] > fieldcount or (
                    pattern['max_fields'] > 0 and pattern['max_fields'] < fieldcount
                ):
                    continue

                field_idxlist = []
                if pattern['field'] is not None:
                    if pattern['field'] == 0:
                        field_idxlist = None
                    else:
                        field_idxlist = [ pyformat.fieldsep.num_to_idx(pattern['field']) ]
                else:
                    field_idxlist = range(0, len(spl), 2)

                if 'replace_all' in pattern:
                    if field_idxlist is not None:
                        for field_idx in field_idxlist:
                            if re.search(pattern['regex'], spl[field_idx]):
                                newdata = pyformat.format_string(
                                    pattern['replace_all'].decode('utf-8'),
                                    context={
                                        'fields': spl
                                    }
                                ).encode('utf-8')

                                spl = re_split(sep.encode('utf-8'), newdata)
                                field_idx_set = set()
                    else:
                        if re.search(pattern['regex'], b''.join(spl)):
                            newdata = pyformat.format_string(
                                pattern['replace_all'].decode('utf-8'),
                                context={
                                    'fields': spl
                                }
                            ).encode('utf-8')

                            spl = re_split(sep.encode('utf-8'), newdata)
                            field_idx_set = set()
                elif 'replace' in pattern:
                    if field_idxlist is not None:
                        for field_idx in field_idxlist:
                            if field_idx in field_idx_set:
                                continue

                            newfield, replace_ranges = pat_schrep(
                                pattern,
                                spl[field_idx],
                                pattern['replace']
                            )
                            if len(replace_ranges) > 0:
                                spl[field_idx] = newfield
                                field_idx_set.add(field_idx)
                    else:
                        newdata, replace_ranges = pat_schrep(
                            pattern,
                            b''.join(spl),
                            pattern['replace']
                        )
                        if len(replace_ranges) > 0:
                            spl = re_split(sep.encode('utf-8'), newdata)
                            field_idx_set = set()

            newdata = b''.join(spl)

        if len(self.current_profile['field_separators']) == 0:
            for pat in self.current_profile['patterns']:
                if pat['activation_line'] > -1 and pat['activation_line'] > self.linecount:
                    continue
                if pat['deactivation_line'] > -1 and pat['deactivation_line'] <= self.linecount:
                    continue

                if pat['filter']:
                    if pat['regex'].search(data):
                        return
                elif 'replace' in pat:
                    newdata, replace_ranges = pat_schrep(pat, newdata, pat['replace'])
                    if len(replace_ranges) > 0:
                        update_ranges(ignore_ranges, replace_ranges)

        stream.buffer.write(newdata)
        stream.flush()

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


def is_being_redirected():
    # https://stackoverflow.com/a/1512526
    return os.fstat(0) != os.fstat(1)

if __name__ == '__main__':
    pycobj = Pycolor()
    args = sys.argv[1:]

    returncode = pycobj.execute(args)
    sys.exit(returncode)
