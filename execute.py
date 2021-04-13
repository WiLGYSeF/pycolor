import fcntl
import os
import signal
import subprocess
import time

from static_vars import static_vars


def nonblock(file):
    fde = file.fileno()
    flag = fcntl.fcntl(fde, fcntl.F_GETFL)
    fcntl.fcntl(fde, fcntl.F_SETFL, flag | os.O_NONBLOCK)

def readlines(stream):
    # file.readlines() is broken
    data = stream.read()
    if data is None or len(data) == 0:
        return None

    lines = []
    last = 0

    for idx in range(len(data)): #pylint: disable=consider-using-enumerate
        if is_eol(data[idx]):
            lines.append(data[last:idx + 1])
            last = idx + 1

    if last < len(data):
        lines.append(data[last:])
    return lines

@static_vars(buffers={})
def read_stream(stream, callback, buffer_line=True, encoding='utf-8', last=False):
    did_callback = False

    def do_callback(data):
        nonlocal did_callback
        did_callback = True
        return callback(data.decode(encoding))

    if stream not in read_stream.buffers:
        read_stream.buffers[stream] = b''

    if buffer_line:
        lines = readlines(stream)
        if lines is None:
            if last and len(read_stream.buffers[stream]) != 0:
                do_callback(read_stream.buffers[stream])
                read_stream.buffers[stream] = b''
            return None

        start = 0
        if is_eol(lines[0][-1]):
            do_callback(read_stream.buffers[stream] + lines[0])
            read_stream.buffers[stream] = b''
            start = 1

        for i in range(start, len(lines) - 1):
            do_callback(lines[i])

        if not is_eol(lines[-1][-1]):
            read_stream.buffers[stream] += lines[-1]

            if last:
                do_callback(read_stream.buffers[stream])
                read_stream.buffers[stream] = b''
        elif len(lines) > 1:
            do_callback(lines[-1])
    else:
        data = stream.read()
        if data is None or len(data) == 0:
            return None

        do_callback(data)

    return did_callback

def is_eol(char):
    ceol = '\n\r'
    for k in ceol:
        if char == ord(k):
            return True
    return False

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
        stderr=subprocess.PIPE
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
            time.sleep(0.000001)

        _read(process.stdout, stdout_callback, last=True)
        _read(process.stdout, stdout_callback, last=True)

        signal.signal(signal.SIGINT, signal.default_int_handler)
        return process.poll()
