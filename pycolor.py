#!/usr/bin/env python3

import fcntl
import json
import os
import re
import sys
import subprocess


def search_replace(pattern, string, replace, ignore_ranges=None):
    if ignore_ranges is None:
        ignore_ranges = []

    newstring = string[:0] #str or bytes
    last = 0
    replace_ranges = []

    if isinstance(pattern, re._pattern_type):
        regex = pattern
    else:
        regex = re.compile(pattern)

    if not callable(replace):
        repl = replace
        replace = lambda x: repl

    igidx = 0

    for match in regex.finditer(string):
        while igidx < len(ignore_ranges) and ignore_ranges[igidx][1] < match.start():
            igidx += 1

        if igidx < len(ignore_ranges):
            ign = ignore_ranges[igidx]
            if any([
                match.start() >= ign[0] and match.start() < ign[1],
                ign[0] >= match.start() and ign[0] < match.end()
            ]):
                continue

        repl = replace(match)
        newstring += string[last:match.start()] + repl
        last = match.end()

        start = match.start()
        end = match.start() + len(repl)

        for rng in replace_ranges:
            old_range, new_range = rng
            diff = new_range[1] - old_range[1] - (new_range[0] - old_range[0])
            start += diff
            end += diff

        replace_ranges.append((
            match.span(),
            (start, end)
        ))

    return newstring + string[last:], replace_ranges

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

            for pattern in self.config['patterns']:
                pattern['regex'] = re.compile(pattern['expression'].encode('utf-8'))
                pattern['replace'] = pattern['replace'].encode('utf-8')

    def execute(self, cmd, buffer_line=True):
        return execute(cmd, self.stdout_cb, self.stderr_cb, buffer_line=buffer_line)

    def stdout_cb(self, data):
        newdata = data

        def replace(repl, match):
            for i in range(len(match.groups())):
                repl = self.backref_regex[i].sub(match[i + 1], repl)
            return repl

        ignore_ranges = []

        for pattern in self.config['patterns']:
            newdata, replace_ranges = search_replace(
                pattern['regex'],
                newdata,
                lambda x: replace(pattern['replace'], x),
                ignore_ranges=ignore_ranges
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
