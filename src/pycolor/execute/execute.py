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
import traceback
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

from ..utils.printmsg import printerr, printwarn
from .threadwait import Flag, ThreadWait

BUFFER_SZ = 4098

Stream = typing.Union[typing.TextIO, io.IOBase, int]

def _readlines(data: bytes) -> typing.Iterator[bytes]:
    """Yields data line by line

    Args:
        data (bytes): Data

    Returns:
        Iterator: Lines from data
    """
    datalen = len(data)
    len_m1 = datalen - 1
    last = 0
    idx = 0

    while idx < datalen:
        ret = _is_eol_idx(data, len_m1, idx)
        if ret is not False:
            yield data[last:ret + 1]
            last = ret + 1
            idx = ret
        idx += 1

    if last < datalen:
        yield data[last:]

_buffers: typing.Dict[Stream, bytes] = {}

def read_stream(
    stream: Stream,
    callback: typing.Callable[[str], None],
    data: bytes,
    encoding: str = 'utf-8',
    last: bool = False
) -> typing.Optional[bool]:
    """Handles buffered stream reading

    Args:
        stream (Stream): Used only for storing bufferred data, not used for reading
        callback (function): Callback function called with stream data line by line
        data (bytes): Stream data
        encoding (str): Stream data to string encoding for callback, default 'utf-8'
        last (bool): Indicates if this will be the last call to read_stream for the stream

    Returns:
        bool: Returns true if the callback function was called, or None if EOF was reached
    """
    did_callback = False

    def do_callback(data: bytes) -> None:
        nonlocal did_callback
        did_callback = True
        return callback(data.decode(encoding))

    if stream not in _buffers:
        _buffers[stream] = b''

    try:
        lines = _readlines(data)
        curline = next(lines)
        if _is_eol(curline[-1]):
            do_callback(_buffers[stream] + curline)
            _buffers[stream] = b''

        for curline in lines:
            if _is_eol(curline[-1]):
                do_callback(curline)
        if not _is_eol(curline[-1]):
            if last:
                do_callback(_buffers[stream] + curline)
                _buffers[stream] = b''
            else:
                _buffers[stream] += curline
    except StopIteration:
        if last and len(_buffers[stream]) != 0:
            do_callback(_buffers[stream])
            _buffers[stream] = b''
        return None
    return did_callback

def _is_buffer_empty(stream: Stream) -> bool:
    """Checks if the stream buffer is empty

    Args:
        stream (Stream): Stream

    Returns:
        bool: Returns true if the stream buffer is empty
    """
    return stream not in _buffers or len(_buffers[stream]) == 0

def _is_eol(char: int) -> bool:
    """Checks if the char is EOL

    Args:
        char (int): Character

    Returns:
        bool: Returns true if char is EOL
    """
    # '\n' and '\r'
    return char == 10 or char == 13 #pylint: disable=consider-using-in

def _is_eol_idx(string: bytes, len_m1: int, idx: int) -> typing.Union[bool, int]:
    """Checks if the character at string index is EOL

    Will check if the character at index is '\r', '\n', or '\r' and the next char is '\n'.

    Args:
        string (bytes): String
        len_m1 (int): Last index of string
        idx (int): Index of string to check for EOL

    Returns:
        int: Index of end EOL character, or False if not an EOL
    """
    char = string[idx]
    if idx < len_m1 and char == 13 and string[idx + 1] == 10:
        return idx + 1
    return idx if _is_eol(char) else False

def execute(
    cmd: typing.List[str],
    stdout_callback: typing.Callable[[str], None],
    stderr_callback: typing.Callable[[str], None],
    **kwargs
) -> int:
    """Executes the command

    Args:
        cmd (list): Command and arguments
        stdout_callback (function): Callback function for stream data from stdout
        stderr_callback (function): Callback function for stream data from stderr

        tty (bool): Enable TTY mode
        encoding (str): Stream data to string encoding for callback, default 'utf-8'
        nobuffer (bool): Enable nobuffer mode
        stdin (Stream): Stdin stream, defaults to sys.stdin

    Returns:
        int: Return code of command
    """
    tty: bool = kwargs.get('tty', False)
    encoding: str = kwargs.get('encoding', 'utf-8')
    nobuffer: bool = kwargs.get('nobuffer', False)
    stdout: Stream
    stderr: Stream
    stdin: Stream = kwargs.get('stdin', sys.stdin)

    if tty and not HAS_PTY:
        printwarn('tty is not supported on this system')
        tty = False

    def _read(
        stream: Stream,
        callback: typing.Callable[[str], None],
        data: bytes,
        last: bool = False
    ) -> typing.Optional[bool]:
        return read_stream(
            stream,
            callback,
            data,
            encoding=encoding,
            last=last
        )

    if tty:
        # https://stackoverflow.com/a/31953436
        masters, slaves = zip(pty.openpty(), pty.openpty())

    returncode = 0

    with ExitStack() as stack:
        stack.enter_context(_ignore_sigint())

        if tty:
            stdout, stderr = masters
            proc_stdout, proc_stderr = slaves
            stack.enter_context(_sync_sigwinch(stdout))
            stack.enter_context(_sync_sigwinch(stderr))
        else:
            proc_stdout = subprocess.PIPE
            proc_stderr = subprocess.PIPE

        with subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=proc_stdout,
            stderr=proc_stderr
        ) as process:
            if not tty:
                stdout = process.stdout
                stderr = process.stderr

            def read_thread(
                stream: Stream,
                callback: typing.Callable[[str], None],
                flag: Flag
            ) -> None:
                while True:
                    flag.unset()
                    data = _read_stream(stream)
                    try:
                        if data is None or _read(stream, callback, data) is None:
                            break
                        if nobuffer and not _is_buffer_empty(stream):
                            _read(stream, callback, b'', last=True)
                    except Exception:
                        printerr('pycolor error, continuing...', traceback.format_exc(), sep='\n')
                _read(stream, callback, b'', last=True)

            def write_stdin(flag: Flag) -> None:
                if process.stdin is None:
                    return

                while True:
                    flag.unset()
                    recv = _read_stream(stdin)
                    if recv is None:
                        break

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

            val = process.poll()
            returncode = val if isinstance(val, int) else 0
    return returncode

def _read_stream(stream: Stream) -> typing.Optional[bytes]:
    if isinstance(stream, (typing.TextIO, io.IOBase)):
        try:
            data = os.read(stream.fileno(), BUFFER_SZ)
        except OSError:
            result = stream.read()
            if not isinstance(result, bytes):
                data = result.encode()
            else:
                data = result
        except ValueError:
            return None
    else:
        try:
            data = os.read(stream, BUFFER_SZ)
        except (OSError, ValueError):
            return None
    return data if data is not None and len(data) > 0 else None

@contextmanager
def _ignore_sigint():
    try:
        signal.signal(signal.SIGINT, lambda x,y: None)
        yield
    finally:
        signal.signal(signal.SIGINT, signal.default_int_handler)

@contextmanager
def _sync_sigwinch(tty_fd: int):
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
