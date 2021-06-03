from contextlib import contextmanager, ExitStack
import errno
import fcntl
import io
import os
import pty
import select
import shutil
import signal
import struct
import subprocess
import sys
import termios
import time

from static_vars import static_vars


def nonblock(file):
    # TODO: not compatible with windows
    fde = file.fileno()
    flag = fcntl.fcntl(fde, fcntl.F_GETFL)
    fcntl.fcntl(fde, fcntl.F_SETFL, flag | os.O_NONBLOCK)

def readlines(stream, data=None):
    if data is None:
        if isinstance(stream, int):
            file = io.FileIO(stream, closefd=False)
            data = file.read()
            file.close()
        else:
            data = stream.read()
    if data is None or len(data) == 0:
        return None

    lines = []
    last = 0

    datalen = len(data)
    idx = 0
    while idx < datalen:
        ret = is_eol_idx(data, idx)
        if ret is not False:
            lines.append(data[last:ret + 1])
            last = ret + 1
            idx = ret
        idx += 1

    if last < datalen:
        lines.append(data[last:])
    return lines

@static_vars(buffers={})
def read_stream(stream, callback, data=None, encoding='utf-8', last=False):
    did_callback = False

    def do_callback(data):
        nonlocal did_callback
        did_callback = True
        return callback(data.decode(encoding))

    if stream not in read_stream.buffers:
        read_stream.buffers[stream] = b''

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

    return did_callback

def is_buffer_empty(stream):
    if stream not in read_stream.buffers:
        return True
    return len(read_stream.buffers[stream]) == 0

def is_eol(char):
    # '\n' and '\r'
    return char == 10 or char == 13 #pylint: disable=consider-using-in

def is_eol_idx(string, idx):
    char = string[idx]
    if idx < len(string) - 1 and char == 13 and string[idx + 1] == 10:
        return idx + 1
    return idx if is_eol(char) else False

def execute(cmd, stdout_callback, stderr_callback, **kwargs):
    tty = kwargs.get('tty', False)
    encoding = kwargs.get('encoding', 'utf-8')
    interactive = kwargs.get('interactive', False)

    def _read(stream, callback, data=None, last=False):
        return read_stream(
            stream,
            callback,
            data=data,
            encoding=encoding,
            last=last
        )

    if tty:
        # https://stackoverflow.com/a/31953436
        masters, slaves = zip(pty.openpty(), pty.openpty())

    with ExitStack() as stack:
        stack.enter_context(ignore_sigint())

        if tty:
            stack.enter_context(sync_sigwinch(masters[0]))
            stack.enter_context(sync_sigwinch(masters[1]))

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=slaves[0],
                stderr=slaves[1]
            )
            stdout = masters[0]
            stderr = masters[1]
        else:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout = process.stdout
            stderr = process.stderr

            try:
                nonblock(stdout)
                nonblock(stderr)
            except AttributeError:
                pass
            except io.UnsupportedOperation:
                pass

        stdin = sys.stdin
        # TODO: io does not like unblocked data
        # this works because we ignore the TypeError expection thrown and
        # is needed in order to not hang on stdin
        # see https://bugs.python.org/issue13322
        nonblock(stdin)

        readable = {
            stdout: stdout_callback,
            stderr: stderr_callback,
            stdin: None
        }

        while readable and process.poll() is None:
            # TODO: not compatible with windows
            for fde in select.select(readable, [], [], 0.1)[0]:
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
                        if fde is stdin:
                            try:
                                recv = stdin.read().encode()
                                process.stdin.write(recv)
                                process.stdin.flush()
                            except BrokenPipeError:
                                break
                            except TypeError:
                                break
                        else:
                            _read(fde, readable[fde], data=data)
                    else:
                        del readable[fde]

            if interactive and not is_buffer_empty(stdout):
                if tty:
                    _read(stdout, stdout_callback, data=b'', last=True)
                else:
                    _read(stdout, stdout_callback, last=True)
            time.sleep(0.0001)

        if tty:
            for fde in slaves:
                os.close(fde)
            for fde in masters:
                os.close(fde)

            _read(stdout, stdout_callback, data=b'', last=True)
            _read(stderr, stderr_callback, data=b'', last=True)
        else:
            _read(stdout, stdout_callback, last=True)
            _read(stderr, stderr_callback, last=True)

        process.stdin.close()

        return process.poll()

@contextmanager
def ignore_sigint():
    try:
        signal.signal(signal.SIGINT, lambda x,y: None)
        yield
    finally:
        signal.signal(signal.SIGINT, signal.default_int_handler)

@contextmanager
def sync_sigwinch(tty_fd):
    # TODO: not compatible with windows
    def set_window_size():
        col, row = shutil.get_terminal_size()
        # https://stackoverflow.com/a/6420070
        winsize = struct.pack('HHHH', row, col, 0, 0)
        fcntl.ioctl(tty_fd, termios.TIOCSWINSZ, winsize)

    try:
        set_window_size()
        signal.signal(signal.SIGWINCH, lambda x,y: set_window_size())
        yield
    finally:
        signal.signal(signal.SIGWINCH, lambda x,y: None)
