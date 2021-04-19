from contextlib import contextmanager
import errno
import fcntl
import os
import pty
import select
import signal
import subprocess
import time

from static_vars import static_vars


def nonblock(file):
    # TODO: not compatible with windows
    fde = file.fileno()
    flag = fcntl.fcntl(fde, fcntl.F_GETFL)
    fcntl.fcntl(fde, fcntl.F_SETFL, flag | os.O_NONBLOCK)

def readlines(stream, data=None):
    if data is None:
        data = stream.read()
    if data is None or len(data) == 0:
        return None

    lines = []
    last = 0

    idx = 0
    while idx < len(data):
        ret = is_eol_idx(data, idx)
        if ret is not False:
            lines.append(data[last:ret + 1])
            last = ret + 1
            idx = ret
        idx += 1

    if last < len(data):
        lines.append(data[last:])
    return lines

@static_vars(buffers={})
def read_stream(stream, callback, data=None, buffer_line=True, encoding='utf-8', last=False):
    did_callback = False

    def do_callback(data):
        nonlocal did_callback
        did_callback = True
        return callback(data.decode(encoding))

    if stream not in read_stream.buffers:
        read_stream.buffers[stream] = b''

    if buffer_line:
        lines = readlines(stream, data)
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
        if data is None:
            data = stream.read()
            if data is None or len(data) == 0:
                return None

        do_callback(data)

    return did_callback

def is_eol(char):
    # '\n' and '\r'
    return char == 10 or char == 13 #pylint: disable=consider-using-in

def is_eol_idx(string, idx):
    if idx < len(string) - 1 and string[idx] == 13 and string[idx + 1] == 10:
        return idx + 1
    return idx if is_eol(string[idx]) else False

def execute(cmd, stdout_callback, stderr_callback, **kwargs):
    buffer_line = kwargs.get('buffer_line', True)
    tty = kwargs.get('tty', False)
    encoding = kwargs.get('encoding', 'utf-8')

    def _read(stream, callback, data=None, last=False):
        return read_stream(
            stream,
            callback,
            data=data,
            buffer_line=buffer_line,
            encoding=encoding,
            last=last
        )

    if tty:
        # https://stackoverflow.com/a/31953436
        masters, slaves = zip(pty.openpty(), pty.openpty())

    with ignore_sigint():
        if tty:
            process = subprocess.Popen(cmd, stdin=slaves[0], stdout=slaves[0], stderr=slaves[1])
            stdout = masters[0]
            stderr = masters[1]
        else:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = process.stdout
            stderr = process.stderr

            nonblock(stdout)
            nonblock(stderr)

        if tty:
            for fde in slaves:
                os.close(fde) # no input

        readable = {
            stdout: stdout_callback,
            stderr: stderr_callback
        }

        while readable and process.poll() is None:
            # TODO: not compatible with windows
            for fde in select.select(readable, [], [])[0]:
                do_read = False
                try:
                    if isinstance(fde, int):
                        data = os.read(fde, 1024)
                        do_read = True
                    else:
                        data = None
                        do_read = True
                except OSError as ose:
                    if ose.errno != errno.EIO:
                        raise
                    del readable[fde]
                else:
                    if do_read:
                        _read(fde, readable[fde], data=data)
                    else:
                        del readable[fde]
            time.sleep(0.001)

        if tty:
            for fde in masters:
                os.close(fde)

            _read(stdout, stdout_callback, data=b'', last=True)
            _read(stderr, stderr_callback, data=b'', last=True)
        else:
            _read(stdout, stdout_callback, last=True)
            _read(stderr, stderr_callback, last=True)

        return process.poll()

@contextmanager
def ignore_sigint():
    def signal_handler(sig, frame):
        pass

    try:
        signal.signal(signal.SIGINT, signal_handler)
        yield
    finally:
        signal.signal(signal.SIGINT, signal.default_int_handler)
