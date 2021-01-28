import fcntl
import os
import subprocess

from static_vars import static_vars


def nonblock(file):
    fde = file.fileno()
    flag = fcntl.fcntl(fde, fcntl.F_GETFL)
    fcntl.fcntl(fde, fcntl.F_SETFL, flag | os.O_NONBLOCK)

def readlines(stream):
    #file.readlines() is broken
    data = stream.read()
    if data is None or len(data) == 0:
        return None

    lines = []
    last = 0

    for idx in range(len(data)): #pylint: disable=consider-using-enumerate
        if data[idx] == ord('\n'):
            lines.append(data[last:idx + 1])
            last = idx + 1

    if last < len(data):
        lines.append(data[last:])
    return lines

@static_vars(buffers={})
def read_stream(stream, callback, buffer_line=True, last=False):
    did_callback = False

    if stream not in read_stream.buffers:
        read_stream.buffers[stream] = b''

    if buffer_line:
        lines = readlines(stream)
        if lines is None:
            if last and len(read_stream.buffers[stream]) != 0:
                callback(read_stream.buffers[stream])
                read_stream.buffers[stream] = b''

            return None

        start = 0

        if lines[0][-1] == ord('\n'):
            callback(read_stream.buffers[stream] + lines[0])
            did_callback = True

            read_stream.buffers[stream] = b''
            start = 1

        for i in range(start, len(lines) - 1):
            callback(lines[i])
            did_callback = True

        if lines[-1][-1] != ord('\n'):
            read_stream.buffers[stream] += lines[-1]

            if last:
                callback(read_stream.buffers[stream])
                did_callback = True

                read_stream.buffers[stream] = b''
        elif len(lines) > 1:
            callback(lines[-1])
            did_callback = True
    else:
        data = stream.read()
        if data is None or len(data) == 0:
            return None

        callback(data)
        did_callback = True

    return did_callback

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
