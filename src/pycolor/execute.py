from contextlib import contextmanager, ExitStack
import io
import os
import shutil
import signal
import struct
import subprocess
import sys
import time
import threading

try:
    import fcntl
    import termios
    HAS_FCNTL = True
except ModuleNotFoundError:
    HAS_FCNTL = False

try:
    import pty
    HAS_PTY = True
except ModuleNotFoundError:
    HAS_PTY = False

from .printmsg import printwarn
from .static_vars import static_vars
from .threadwait import ThreadWait


BUFFER_SZ = 4098


def readlines(stream, data=None):
    if data is None:
        data = stream.read()
    if data is None or len(data) == 0:
        return None

    lines = []
    last = 0

    datalen = len(data)
    len_m1 = datalen - 1
    idx = 0
    while idx < datalen:
        ret = is_eol_idx(data, len_m1, idx)
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

def is_eol_idx(string, len_m1, idx):
    char = string[idx]
    if idx < len_m1 and char == 13 and string[idx + 1] == 10:
        return idx + 1
    return idx if is_eol(char) else False

def execute(cmd, stdout_callback, stderr_callback, **kwargs):
    tty = kwargs.get('tty', False)
    encoding = kwargs.get('encoding', 'utf-8')
    interactive = kwargs.get('interactive', False)
    stdin = kwargs.get('stdin', sys.stdin)

    if tty and not HAS_PTY:
        printwarn('tty is not supported on this system')
        tty = False

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

        def read_thread(stream, callback, flag):
            if isinstance(stream, io.IOBase):
                try:
                    stream = stream.fileno()
                except OSError:
                    pass

            use_os_read = isinstance(stream, int)
            while True:
                flag.unset()
                if use_os_read:
                    try:
                        data = os.read(stream, BUFFER_SZ)
                    except OSError:
                        break
                    if len(data) == 0 or _read(stream, callback, data=data) is None:
                        break
                    if interactive and not is_buffer_empty(stream):
                        _read(stream, callback, data=b'', last=True)
                else:
                    if _read(stream, callback) is None:
                        break
                    if interactive and not is_buffer_empty(stream):
                        _read(stream, callback, last=True)

        def write_stdin(flag):
            stream = stdin
            if isinstance(stream, io.IOBase):
                try:
                    stream = stream.fileno()
                except OSError:
                    pass

            use_os_read = isinstance(stream, int)
            while True:
                flag.unset()
                if use_os_read:
                    recv = os.read(stream, BUFFER_SZ)
                    if len(recv) == 0:
                        break
                else:
                    recv = stdin.read()
                    if recv is None or len(recv) == 0:
                        break
                    recv = recv.encode()

                process.stdin.write(recv)
                process.stdin.flush()
            process.stdin.close()

        wait = ThreadWait()
        thr_stdout = threading.Thread(target=read_thread, args=(
            stdout,
            stdout_callback,
            wait.get_flag(),
        ), daemon=True)
        thr_stderr = threading.Thread(target=read_thread, args=(
            stderr,
            stderr_callback,
            wait.get_flag(),
        ), daemon=True)
        thr_stdin = threading.Thread(target=write_stdin, args=(
            wait.get_flag(),
        ), daemon=True)

        thr_stdout.start()
        thr_stderr.start()
        thr_stdin.start()

        # TODO: this is probably not the best way to wait
        while process.poll() is None:
            time.sleep(0.001)
        wait.wait(timeout=0.075)

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
    # Unix only
    if not HAS_FCNTL or not hasattr(signal, 'SIGWINCH'):
        return

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
