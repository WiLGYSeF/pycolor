#!/usr/bin/env python3

import json
import re
import sys

from execute import execute
from search_replace import search_replace, update_ranges
from which import which


PYCOLOR_CONFIG_FNAME = 'config.json'

class Pycolor:
    def __init__(self):
        self.profiles = []

        with open(PYCOLOR_CONFIG_FNAME, 'r') as file:
            config = json.loads(file.read())

            for prof_cfg in config.get('profiles', []):
                profile = {
                    'name': prof_cfg.get('name'),
                    'profile_name': prof_cfg.get('profile_name'),
                    'which': prof_cfg.get('which'),
                    'buffer_line': prof_cfg.get('buffer_line', True),
                    'from_profiles': prof_cfg.get('from_profiles', []),
                    'patterns': []
                }

                for pattern_cfg in prof_cfg.get('patterns', []):
                    if 'expression' not in pattern_cfg:
                        raise Exception()
                        continue

                    pattern = {
                        'expression': pattern_cfg['expression'],
                        'regex': re.compile(pattern_cfg['expression'].encode('utf-8')),
                    }

                    if 'replace' in pattern_cfg:
                        pattern['replace'] = pattern_cfg['replace'].encode('utf-8')
                    profile['patterns'].append(pattern)

                self.profiles.append(profile)

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
            elif command == cfg['name']:
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
            stdout_cb = self.stdout_base_cb
            stderr_cb = self.stderr_base_cb

        return execute(
            cmd,
            stdout_cb,
            stderr_cb,
            buffer_line=self.current_profile.get('buffer_line', True)
        )

    def data_callback(self, stream, data):
        newdata = data
        ignore_ranges = []

        for pattern in self.current_profile['patterns']:
            if pattern.get('filter', False):
                if pattern['regex'].search(data):
                    return
            elif 'replace' in pattern:
                newdata, replace_ranges = search_replace(
                    pattern['regex'],
                    newdata,
                    lambda x: x.expand(pattern['replace']),
                    ignore_ranges=ignore_ranges,
                    start_occurrance=pattern.get('start_occurrance', 1),
                    max_count=pattern.get('max_count', -1)
                )
                if len(replace_ranges) > 0:
                    update_ranges(ignore_ranges, replace_ranges)

        stream.buffer.write(newdata)
        stream.flush()

    def stdout_cb(self, data):
        self.data_callback(sys.stdout, data)

    def stderr_cb(self, data):
        self.data_callback(sys.stderr, data)

    def stdout_base_cb(self, data):
        sys.stdout.buffer.write(data)
        sys.stdout.flush()

    def stderr_base_cb(self, data):
        sys.stderr.buffer.write(data)
        sys.stderr.flush()


if __name__ == '__main__':
    pycobj = Pycolor()
    args = sys.argv[1:]

    result = pycobj.execute(args)
    sys.exit(result)
