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
import typing

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
from .threadwait import Flag, ThreadWait

BUFFER_SZ = 4098

_Stream = typing.Union[io.IOBase, int]

def _readlines(stream: io.IOBase, data: bytes = None) -> typing.Optional[typing.List[bytes]]:
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
        ret = _is_eol_idx(data, len_m1, idx)
        if ret is not False:
            lines.append(data[last:ret + 1])
            last = ret + 1
            idx = ret
        idx += 1

    if last < datalen:
        lines.append(data[last:])
    return lines

_buffers: typing.Dict[_Stream, bytes] = {}

def read_stream(
    stream: io.IOBase,
    callback: typing.Callable[[str], None],
    data: bytes = None,
    encoding: str = 'utf-8',
    last: bool = False
) -> typing.Optional[bool]:
    did_callback = False

    def do_callback(data: bytes) -> None:
        nonlocal did_callback
        did_callback = True
        return callback(data.decode(encoding))

    if stream not in _buffers:
        _buffers[stream] = b''

    lines = _readlines(stream, data)
    if lines is None:
        if last and len(_buffers[stream]) != 0:
            do_callback(_buffers[stream])
            _buffers[stream] = b''
        return None

    start = 0
    if _is_eol(lines[0][-1]):
        do_callback(_buffers[stream] + lines[0])
        _buffers[stream] = b''
        start = 1

    for i in range(start, len(lines) - 1):
        do_callback(lines[i])

    if not _is_eol(lines[-1][-1]):
        _buffers[stream] += lines[-1]

        if last:
            do_callback(_buffers[stream])
            _buffers[stream] = b''
    elif len(lines) > 1:
        do_callback(lines[-1])

    return did_callback

def _is_buffer_empty(stream: _Stream) -> bool:
    if stream not in _buffers:
        return True
    return len(_buffers[stream]) == 0

def _is_eol(char: int) -> bool:
    # '\n' and '\r'
    return char == 10 or char == 13 #pylint: disable=consider-using-in

def _is_eol_idx(string: bytes, len_m1: int, idx: int) -> typing.Union[bool, int]:
    char = string[idx]
    if idx < len_m1 and char == 13 and string[idx + 1] == 10:
        return idx + 1
    return idx if _is_eol(char) else False

def execute(
    cmd: typing.List[str],
    stdout_callback: typing.Callable[[str], None],
    stderr_callback: typing.Callable[[str], None],
    **kwargs
) -> typing.Optional[int]:
    tty: bool = kwargs.get('tty', False)
    encoding: str = kwargs.get('encoding', 'utf-8')
    interactive: bool = kwargs.get('interactive', False)
    stdout: _Stream
    stderr: _Stream
    stdin: _Stream = kwargs.get('stdin', sys.stdin)

    if tty and not HAS_PTY:
        printwarn('tty is not supported on this system')
        tty = False

    def _read(
        stream: io.IOBase,
        callback: typing.Callable[[str], None],
        data: bytes = None,
        last: bool = False
    ) -> bool:
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
        stack.enter_context(_ignore_sigint())

        if tty:
            stdout, stderr = masters
            stack.enter_context(_sync_sigwinch(stdout))
            stack.enter_context(_sync_sigwinch(stderr))
            proc_stdout, proc_stderr = slaves
        else:
            proc_stdout = subprocess.PIPE
            proc_stderr = subprocess.PIPE

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=proc_stdout,
            stderr=proc_stderr
        )

        if not tty:
            stdout = process.stdout
            stderr = process.stderr

        def read_thread(
            stream: _Stream,
            callback: typing.Callable[[str], None],
            flag: Flag
        ) -> None:
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
                    if interactive and not _is_buffer_empty(stream):
                        _read(stream, callback, data=b'', last=True)
                else:
                    if _read(stream, callback) is None:
                        break
                    if interactive and not _is_buffer_empty(stream):
                        _read(stream, callback, last=True)

        def write_stdin(flag: Flag) -> None:
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
    return None

@contextmanager
def _ignore_sigint():
    try:
        signal.signal(signal.SIGINT, lambda x,y: None)
        yield
    finally:
        signal.signal(signal.SIGINT, signal.default_int_handler)

@contextmanager
def _sync_sigwinch(tty_fd: int) -> None:
    # Unix only
    if not HAS_FCNTL or not hasattr(signal, 'SIGWINCH'):
        return

    def set_window_size() -> None:
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
