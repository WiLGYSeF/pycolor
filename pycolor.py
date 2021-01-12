#!/usr/bin/env python3

import json
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
            for fromprof_cfg in profile['from_profiles']:
                if isinstance(fromprof_cfg, dict):
                    if len(fromprof_cfg.get('name', '')) == 0:
                        raise Exception()

                    fromprof = self.get_profile_by_name(fromprof_cfg['name'])
                    if fromprof is None:
                        raise Exception()

                    if 'order' in fromprof_cfg:
                        if fromprof_cfg['order'] not in ('before', 'after'):
                            raise Exception()

                        if fromprof_cfg['order'] == 'before':
                            profile['patterns'] = fromprof['patterns'] + profile['patterns']
                        elif fromprof_cfg['order'] == 'after':
                            profile['patterns'].extend(fromprof['patterns'])
                    else:
                        profile['patterns'].extend(fromprof['patterns'])
                elif isinstance(fromprof_cfg, str):
                    fromprof = self.get_profile_by_name(fromprof_cfg)
                    if fromprof is None:
                        raise Exception()

                    profile['patterns'].extend(fromprof['patterns'])
                else:
                    raise Exception()

        self.current_profile = {}

    def parse_file(self, file):
        config = json.loads(file.read())

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
                if 'expression' not in pattern_cfg:
                    raise Exception()
                    continue

                pattern = {
                    'expression': pattern_cfg['expression'],
                    'regex': re.compile(pattern_cfg['expression'].encode('utf-8')),
                    'filter': pattern_cfg.get('filter', False),
                    'start_occurrance': 1,
                    'max_count': -1
                }

                if 'replace' in pattern_cfg:
                    pattern['replace'] = pyformat.format_string(
                        pattern_cfg['replace']
                    ).encode('utf-8')
                profile['patterns'].append(pattern)

            for fieldsep_cfg in prof_cfg.get('field_separators', []):
                if 'separator' not in fieldsep_cfg:
                    raise Exception()
                    continue

                fieldsep = {
                    'separator': fieldsep_cfg['separator'],
                    'patterns': []
                }

                for pattern_cfg in fieldsep_cfg.get('patterns', []):
                    if 'expression' not in pattern_cfg:
                        raise Exception()
                        continue

                    pattern = {
                        'field': pattern_cfg.get('field'),
                        'min_fields': pattern_cfg.get('min_fields', -1),
                        'expression': pattern_cfg['expression'],
                        'regex': re.compile(pattern_cfg['expression'].encode('utf-8')),
                        'filter': pattern_cfg.get('filter', False),
                        'start_occurrance': 1,
                        'max_count': -1
                    }

                    if 'replace' in pattern_cfg:
                        pattern['replace'] = pyformat.format_string(
                            pattern_cfg['replace']
                        ).encode('utf-8')
                    if 'replace_all' in pattern_cfg:
                        pattern['replace_all'] = pyformat.format_string(
                            pattern_cfg['replace_all']
                        ).encode('utf-8')
                    fieldsep['patterns'].append(pattern)

                profile['field_separators'].append(fieldsep)

            self.profiles.append(profile)

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
            print('no config') # TODO: remove
            self.current_profile = {}
            stdout_cb = Pycolor.stdout_base_cb
            stderr_cb = Pycolor.stderr_base_cb

        return execute.execute(
            cmd,
            stdout_cb,
            stderr_cb,
            buffer_line=self.current_profile['buffer_line']
        )

    def data_callback(self, stream, data):
        newdata = data
        ignore_ranges = []

        for fieldsep in self.current_profile['field_separators']:
            sep = fieldsep['separator']
            spl = re_split(sep.encode('utf-8'), newdata)
            field_idx_set = set()

            for pattern in fieldsep['patterns']:
                if pattern['min_fields'] >= pyformat.fieldsep.idx_to_num(len(spl)):
                    continue

                if 'replace_all' in pattern:
                    field_idx = pyformat.fieldsep.num_to_idx(pattern['field'])
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
                    if pattern['field'] is not None:
                        field_idxlist = [pyformat.fieldsep.num_to_idx(pattern['field'])]
                    else:
                        field_idxlist = range(pyformat.fieldsep.idx_to_num(len(spl)))

                    for field_idx in field_idxlist:
                        if field_idx in field_idx_set:
                            continue

                        newfield, replace_ranges = search_replace(
                            pattern['expression'].encode('utf-8'),
                            spl[field_idx],
                            lambda x: pyformat.format_string(
                                pattern['replace'].decode('utf-8'),
                                context={
                                    'match': x
                                }
                            ).encode('utf-8'),
                            ignore_ranges=[],
                            start_occurrance=pattern['start_occurrance'],
                            max_count=pattern['max_count']
                        )
                        if len(replace_ranges) > 0:
                            spl[field_idx] = newfield
                            field_idx_set.add(field_idx)

            newdata = b''.join(spl)

        if len(self.current_profile['field_separators']) == 0:
            for pattern in self.current_profile['patterns']:
                if pattern['filter']:
                    if pattern['regex'].search(data):
                        return
                elif 'replace' in pattern:
                    newdata, replace_ranges = search_replace(
                        pattern['regex'],
                        newdata,
                        lambda x: pyformat.format_string(
                            pattern['replace'].decode('utf-8'),
                            context={
                                'match': x
                            }
                        ).encode('utf-8'),
                        ignore_ranges=ignore_ranges,
                        start_occurrance=pattern['start_occurrance'],
                        max_count=pattern['max_count']
                    )
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


if __name__ == '__main__':
    pycobj = Pycolor()
    args = sys.argv[1:]

    returncode = pycobj.execute(args)
    sys.exit(returncode)
