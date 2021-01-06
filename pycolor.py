#!/usr/bin/env python3

import fcntl
import json
import os
import re
import sys
import subprocess

from search_replace import search_replace
from which import which

def update_ranges(ranges, replace_ranges):
    for ridx in range(len(ranges)): #pylint: disable=consider-using-enumerate
        cur = ranges[ridx]
        start, end = cur

        for replidx in range(len(replace_ranges) - 1, -1, -1):
            old_range, new_range = replace_ranges[replidx]

            if cur[0] >= old_range[1]:
                diff = new_range[1] - old_range[1] - (new_range[0] - old_range[0])
                start += diff
                end += diff

        ranges[ridx] = (start, end)

    ranges.extend(map(lambda x: x[1], replace_ranges))
    ranges.sort(key=lambda x: x[0])

class Pycolor:
    def __init__(self):
        self.backref_regex = [
            re.compile(rb'\\%d' % (i + 1)) for i in range(10)
        ]

        with open('config.json', 'r') as file:
            self.config = json.loads(file.read())

            for program in self.config['programs']:
                for pattern in program['patterns']:
                    pattern['regex'] = re.compile(pattern['expression'].encode('utf-8'))
                    pattern['replace'] = pattern['replace'].encode('utf-8')

        self.program_config = None

    def execute(self, cmd, buffer_line=True):
        self.program_config = None

        for cfg in self.config['programs']:
            if 'which' in cfg:
                if which(cmd[0]).decode('utf-8') == cfg['which']:
                    self.program_config = cfg
            elif cmd[0] == cfg['name']:
                self.program_config = cfg

        if self.program_config is not None:
            stdout_cb = self.stdout_cb
            stderr_cb = self.stderr_cb
        else:
            print('no config')
            stdout_cb = lambda x: sys.stdout.buffer.write(x) and sys.stdout.flush()
            stderr_cb = lambda x: sys.stderr.buffer.write(x) and sys.stderr.flush()

        return execute(cmd, stdout_cb, stderr_cb, buffer_line=buffer_line)

    def stdout_cb(self, data):
        newdata = data
        ignore_ranges = []

        for pattern in self.program_config['patterns']:
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

        sys.stdout.buffer.write(newdata)
        sys.stdout.flush()

    def stderr_cb(self, data):
        data = data.decode('utf-8')
        sys.stderr.write('\x1b[34m' + data + '\x1b[0m')
        sys.stderr.flush()

def nonblock(file):
    fde = file.fileno()
    flag = fcntl.fcntl(fde, fcntl.F_GETFL)
    fcntl.fcntl(fde, fcntl.F_SETFL, flag | os.O_NONBLOCK)

# https://stackoverflow.com/a/279586
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(buffers={})
def read_stream(stream, callback, buffer_line=True, last=False):
    if stream not in read_stream.buffers:
        read_stream.buffers[stream] = b''

    if buffer_line:
        lines = stream.readlines()

        if len(lines) == 0:
            return

        start = 0

        if lines[0][-1] == ord('\n'):
            callback(read_stream.buffers[stream] + lines[0])
            read_stream.buffers[stream] = b''
            start = 1

        for i in range(start, len(lines) - 1):
            callback(lines[i])

        if lines[-1][-1] != ord('\n'):
            read_stream.buffers[stream] += lines[-1]

            if last:
                callback(read_stream.buffers[stream])
                read_stream.buffers[stream] = b''
        elif len(lines) > 1:
            callback(lines[-1])
    else:
        data = stream.read()
        if data:
            callback(data)

def execute(cmd, stdout_callback, stderr_callback, buffer_line=True):
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ) as process:
        nonblock(process.stdout)
        nonblock(process.stderr)

        while process.poll() is None:
            read_stream(process.stdout, stdout_callback, buffer_line=buffer_line)
            read_stream(process.stderr, stderr_callback, buffer_line=buffer_line)

        read_stream(process.stdout, stdout_callback, buffer_line=buffer_line, last=True)
        read_stream(process.stderr, stderr_callback, buffer_line=buffer_line, last=True)

        return process.poll()

if __name__ == '__main__':
    pycobj = Pycolor()
    args = sys.argv[1:]

    result = pycobj.execute(
        args,
        buffer_line=True
    )
    sys.exit(result)
