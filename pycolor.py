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
        with open(PYCOLOR_CONFIG_FNAME, 'r') as file:
            self.config = json.loads(file.read())

            for profile in self.config.get('profiles', []):
                for pattern in profile.get('patterns', []):
                    if 'expression' in pattern:
                        pattern['regex'] = re.compile(pattern['expression'].encode('utf-8'))
                    if 'replace' in pattern:
                        pattern['replace'] = pattern['replace'].encode('utf-8')

        self.profile_cfg = {}

    def execute(self, cmd):
        self.profile_cfg = {}

        for cfg in self.config.get('profiles', []):
            if 'which' in cfg:
                if which(cmd[0]).decode('utf-8') == cfg['which']:
                    self.profile_cfg = cfg
            elif 'name' not in cfg or cmd[0] == cfg['name']:
                self.profile_cfg = cfg

        if len(self.profile_cfg) != 0:
            stdout_cb = self.stdout_cb
            stderr_cb = self.stderr_cb
        else:
            print('no config') # TODO: remove
            stdout_cb = self.stdout_base_cb
            stderr_cb = self.stderr_base_cb

        return execute(
            cmd,
            stdout_cb,
            stderr_cb,
            buffer_line=self.profile_cfg.get('buffer_line', True)
        )

    def data_callback(self, stream, data):
        newdata = data
        ignore_ranges = []

        for pattern in self.profile_cfg.get('patterns', []):
            if 'regex' in pattern:
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
