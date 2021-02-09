from contextlib import contextmanager
import io
import os

from tests.testutils import patch

from execute import read_stream
import pycolor_class


def check_pycolor_execute(
    self,
    cmd,
    mocked_data_dir,
    test_name,
    print_output=False,
    write_output=False
):
    pycobj = pycolor_class.Pycolor(color_mode='always')
    filename_prefix = os.path.join(mocked_data_dir, test_name)
    pycobj.load_file(filename_prefix + '.json')

    def open_fstream(fname):
        try:
            return open(fname, 'rb')
        except FileNotFoundError:
            return None

    def read_file(fname):
        try:
            with open(fname, 'rb') as file:
                return file.read()
        except FileNotFoundError:
            return None

    def write_file(fname, data):
        if len(data) == 0:
            return

        with open(fname, 'wb') as file:
            file.write(data)
            print('Wrote to ' + fname)

    stdout = open_fstream(filename_prefix + '.txt')
    stderr = open_fstream(filename_prefix + '.err.txt')

    output_expected = read_file(filename_prefix + '.out.txt')
    output_expected_err = read_file(filename_prefix + '.out.err.txt')

    pycobj.stdout = io.TextIOWrapper(io.BytesIO())
    pycobj.stderr = io.TextIOWrapper(io.BytesIO())

    with execute_patch(pycolor_class.execute, stdout, stderr):
        pycobj.execute(cmd)

    if stdout is not None:
        stdout.close()
    if stderr is not None:
        stderr.close()

    def test_stream(stream, fname, testdata):
        stream.seek(0)
        data = stream.buffer.read()

        if print_output:
            print(data.decode('utf-8'))
        if write_output:
            write_file(fname, data)

        if testdata is not None:
            self.assertEqual(data, testdata)
        else:
            self.assertEqual(data, b'')

    test_stream(pycobj.stdout, filename_prefix + '.out.txt', output_expected)
    test_stream(pycobj.stderr, filename_prefix + '.out.err.txt', output_expected_err)

@contextmanager
def execute_patch(obj, stdout_stream, stderr_stream):
    def execute(cmd, stdout_callback, stderr_callback, buffer_line=True, encoding='utf-8'):
        def _read(stream, callback, last=False):
            return read_stream(
                stream,
                callback,
                buffer_line=buffer_line,
                encoding=encoding,
                last=last
            )

        while True:
            result_stdout = None
            result_stderr = None

            if stdout_stream is not None:
                result_stdout = _read(stdout_stream, stdout_callback)
            if stderr_stream is not None:
                result_stderr = _read(stderr_stream, stderr_callback)

            if result_stdout is None and result_stderr is None:
                break

        if stdout_stream is not None:
            _read(stdout_stream, stdout_callback, last=True)
        if stderr_stream is not None:
            _read(stderr_stream, stderr_callback, last=True)
        return 0

    with patch(obj, 'execute', execute):
        yield
