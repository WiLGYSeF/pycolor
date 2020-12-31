#!/usr/bin/env python3

import fcntl
import os
import sys
import subprocess

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

def stdout_cb(data):
    data = data.decode('utf-8')
    sys.stdout.write(data)
    sys.stdout.flush()

def stderr_cb(data):
    data = data.decode('utf-8')
    sys.stderr.write(data)
    sys.stderr.flush()

if __name__ == '__main__':
    args = sys.argv[1:]

    result = execute(
        args,
        stdout_cb,
        stderr_cb,
        buffer_line=True
    )
    sys.exit(result)
