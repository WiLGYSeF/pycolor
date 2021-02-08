import fcntl
import os
import signal
import subprocess

from static_vars import static_vars


def nonblock(file):
    fde = file.fileno()
    flag = fcntl.fcntl(fde, fcntl.F_GETFL)
    fcntl.fcntl(fde, fcntl.F_SETFL, flag | os.O_NONBLOCK)

def readlines(stream, encoding='utf-8'):
    # file.readlines() is broken
    try:
        data = stream.read()
        if data is None or len(data) == 0:
            return None
    except TypeError:
        return None

    if isinstance(data, bytes):
        data = data.decode(encoding)

    lines = []
    last = 0

    for idx in range(len(data)): #pylint: disable=consider-using-enumerate
        if data[idx] == '\n':
            lines.append(data[last:idx + 1])
            last = idx + 1

    if last < len(data):
        lines.append(data[last:])
    return lines

@static_vars(buffers={})
def read_stream(stream, callback, buffer_line=True, encoding='utf-8', last=False):
    did_callback = False

    if stream not in read_stream.buffers:
        read_stream.buffers[stream] = ''

    if buffer_line:
        lines = readlines(stream, encoding=encoding)
        if lines is None:
            if last and len(read_stream.buffers[stream]) != 0:
                callback(read_stream.buffers[stream])
                read_stream.buffers[stream] = ''

            return None

        start = 0

        if lines[0][-1] == '\n':
            callback(read_stream.buffers[stream] + lines[0])
            did_callback = True

            read_stream.buffers[stream] = ''
            start = 1

        for i in range(start, len(lines) - 1):
            callback(lines[i])
            did_callback = True

        if lines[-1][-1] != '\n':
            read_stream.buffers[stream] += lines[-1]

            if last:
                callback(read_stream.buffers[stream])
                did_callback = True

                read_stream.buffers[stream] = ''
        elif len(lines) > 1:
            callback(lines[-1])
            did_callback = True
    else:
        try:
            data = stream.read()
            if data is None or len(data) == 0:
                return None
        except TypeError:
            return None

        callback(data.decode(encoding))
        did_callback = True

    return did_callback

def execute(cmd, stdout_callback, stderr_callback, buffer_line=True, encoding='utf-8'):
    def _read(stream, callback, last=False):
        return read_stream(
            stream,
            callback,
            buffer_line=buffer_line,
            encoding=encoding,
            last=last
        )

    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding=encoding
    ) as process:
        def signal_handler(sig, frame):
            # SIGINT is passed through to the subprocess
            pass

        signal.signal(signal.SIGINT, signal_handler)

        nonblock(process.stdout)
        nonblock(process.stderr)

        while process.poll() is None:
            _read(process.stdout, stdout_callback)
            _read(process.stderr, stderr_callback)

        _read(process.stdout, stdout_callback, last=True)
        _read(process.stdout, stdout_callback, last=True)

        signal.signal(signal.SIGINT, signal.default_int_handler)
        return process.poll()
