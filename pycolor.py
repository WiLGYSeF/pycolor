#!/usr/bin/env python3

import fcntl
import json
import os
import re
import sys
import subprocess
from typing import Pattern


def search_replace(pattern, string, callback):
    newstring = string[:0] #str or bytes
    last = 0
    matches = 0

    if isinstance(pattern, Pattern):
        regex = pattern
    else:
        regex = re.compile(pattern)

    for match in regex.finditer(string):
        newstring += string[last:match.start()] + callback(match)
        last = match.end()
        matches += 1

    return newstring + string[last:], matches

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

        for pattern in self.config['patterns']:
            def replace(match):
                repl = pattern['replace']
                for i in range(len(match.groups())):
                    repl = self.backref_regex[i].sub(match[i + 1], repl)
                return repl

            newdata, matches = search_replace(
                pattern['regex'],
                newdata,
                replace
            )
            if matches > 0:
                break

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
