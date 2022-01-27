from contextlib import contextmanager
import io
import os
import typing

from src.pycolor import __main__ as pycolor
from src.pycolor.pycolor import pycolor_class
from src.pycolor.pycolor.pycolor_class import Pycolor
from tests.testutils import patch

def check_pycolor_execute(self,
    cmd: typing.List[str],
    mocked_data_dir: str,
    test_name: str,
    **kwargs
):
    config_file: typing.Optional[str] = kwargs.get('config_file')
    profile_name: typing.Optional[str] = kwargs.get('profile_name')
    print_output: bool = kwargs.get('print_output', False)
    write_output: bool = kwargs.get('write_output', False)
    debug: int = kwargs.get('debug', 0)

    pycobj = create_pycolor_object(debug=debug)
    filename_prefix = os.path.join(mocked_data_dir, test_name)

    if config_file is None:
        config_file = filename_prefix + '.json'
    pycobj.load_file(config_file)

    stdout = open_fstream(filename_prefix + '.txt')
    stderr = open_fstream(filename_prefix + '.err.txt')

    output_expected = read_file(filename_prefix + '.out.txt')
    output_expected_err = read_file(filename_prefix + '.out.err.txt')

    with execute_patch(pycolor_class.execute, stdout, stderr):
        pycobj.execute(
            cmd,
            profile=pycobj.get_profile_by_name(profile_name) if profile_name is not None else None
        )

    if stdout is not None:
        stdout.close()
    if stderr is not None:
        stderr.close()

    test_stream(self,
        pycobj.stdout,
        filename_prefix + '.out.txt',
        output_expected,
        print_output,
        write_output
    )
    test_stream(self,
        pycobj.stderr,
        filename_prefix + '.out.err.txt',
        output_expected_err,
        print_output,
        write_output
    )

def check_pycolor_stdin(self,
    profile_name: str,
    mocked_data_dir: str,
    test_name: str,
    **kwargs
) -> None:
    print_output: bool = kwargs.get('print_output', False)
    write_output: bool = kwargs.get('write_output', False)
    debug: int = kwargs.get('debug', 0)

    pycobj = create_pycolor_object(debug=debug)
    filename_prefix = os.path.join(mocked_data_dir, test_name)
    pycobj.load_file(filename_prefix + '.json')

    stdin_data = read_file(filename_prefix + '.txt')
    stdin = io.TextIOWrapper(io.BytesIO(stdin_data if stdin_data is not None else b''))
    output_expected = read_file(filename_prefix + '.out.txt')

    pycobj.current_profile = pycobj.get_profile_by_name(profile_name)
    pycolor.read_input_stream(pycobj, stdin)

    test_stream(self,
        pycobj.stdout,
        filename_prefix + '.out.txt',
        output_expected,
        print_output,
        write_output
    )

def test_stream(self,
    stream,
    fname: str,
    testdata: typing.Optional[bytes],
    print_output: bool,
    write_output: bool
) -> None:
    stream.seek(0)
    data = stream.buffer.read()

    if print_output: #pragma: no cover
        print(data.decode('utf-8'))
    if write_output: #pragma: no cover
        write_file(fname, data)

    if testdata is not None:
        self.assertEqual(testdata, data)
    else:
        self.assertEqual(b'', data)

def create_pycolor_object(debug: int = 0) -> Pycolor:
    return Pycolor(
        color_mode='always',
        debug=debug,
        stdout=textstream(),
        stderr=textstream()
    )

@contextmanager
def execute_patch(obj, stdout_stream, stderr_stream):
    def popen(args, **kwargs):
        class MockProcess:
            def __init__(self, args, **kwargs):
                self.args = args

                def set_stream(name, stream):
                    res = kwargs.get(name)
                    if isinstance(res, int) and res != -1:
                        if stream is not None:
                            os.write(res, stream.read())
                    else:
                        res = stream if stream else textstream()
                    return res

                self.stdin = set_stream('stdin', None)
                self.stdout = set_stream('stdout', stdout_stream)
                self.stderr = set_stream('stderr', stderr_stream)

                self.returncode: typing.Optional[int] = None
                self.polled: int = 0

            def poll(self) -> typing.Optional[int]:
                if self.polled > 1:
                    self.returncode = 0
                self.polled += 1
                return self.returncode

            def __enter__(self):
                return self

            def __exit__(self, exc_type, val, trbk):
                pass

        return MockProcess(args, **kwargs)

    with patch(getattr(obj, 'subprocess'), 'Popen', popen):
        yield

def textstream() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO())

def open_fstream(fname: str) -> typing.Optional[typing.BinaryIO]:
    try:
        return open(fname, 'rb')
    except FileNotFoundError:
        return None

def read_file(fname: str) -> typing.Optional[bytes]:
    try:
        with open(fname, 'rb') as file:
            return file.read()
    except FileNotFoundError:
        return None

def write_file(fname: str, data: bytes) -> None: #pragma: no cover
    if len(data) == 0:
        return

    with open(fname, 'wb') as file:
        file.write(data)
        print('Wrote to ' + fname)
