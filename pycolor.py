#!/usr/bin/env python3

import fcntl
import os
import sys
import subprocess

def nonblock(file):
    fde = file.fileno()
    flag = fcntl.fcntl(fde, fcntl.F_GETFL)
    fcntl.fcntl(fde, fcntl.F_SETFL, flag | os.O_NONBLOCK)

def execute(cmd, stdout_callback, stderr_callback):
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ) as process:
        nonblock(process.stdout)
        nonblock(process.stderr)

        while process.poll() is None:
            data = process.stdout.read()
            if data:
                stdout_callback(data)
            data = process.stderr.read()
            if data:
                stderr_callback(data)

        return process.poll()

def stdout_cb(data):
    data = data.decode('utf-8')
    sys.stdout.write(data)

def stderr_cb(data):
    sys.stderr.write(data.decode('utf-8'))

args = sys.argv[1:]

result = execute(
    args,
    stdout_cb,
    stderr_cb,
)
sys.exit(result)
