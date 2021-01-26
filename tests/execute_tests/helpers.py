from contextlib import contextmanager
import os

from tests.testutils import patch

from execute import read_stream
import pycolor_class


def check_pycolor_execute(self, cmd, mocked_data_dir, test_name):
    pycobj = pycolor_class.Pycolor()
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

    stdout = open_fstream(filename_prefix + '.txt')
    stderr = open_fstream(filename_prefix + '.err.txt')

    output_expected = read_file(filename_prefix + '.out.txt')
    output_expected_err = read_file(filename_prefix + '.out.err.txt')

    if output_expected is None and output_expected_err is None:
        raise FileNotFoundError(
            '%s is missing expected output test files for: %s' % (mocked_data_dir, test_name)
        )

    output = b''
    output_err = b''

    def stdout_cb(data):
        nonlocal output
        output += data

    def stderr_cb(data):
        nonlocal output_err
        output_err += data

    with execute_patch(pycolor_class.execute, stdout, stderr, stdout_cb, stderr_cb):
        pycobj.execute(cmd)

    if stdout is not None:
        stdout.close()
    if stderr is not None:
        stderr.close()

    if output_expected is not None:
        self.assertEqual(output, output_expected)
    if output_expected_err is not None:
        self.assertEqual(output_err, output_expected_err)

@contextmanager
def execute_patch(obj, stdout_stream, stderr_stream, stdout_cb, stderr_cb):
    def execute(cmd, stdout_callback, stderr_callback, buffer_line=True):
        while True:
            result_stdout = None
            result_stderr = None

            if stdout_stream is not None:
                result_stdout = read_stream(stdout_stream, stdout_cb, buffer_line=buffer_line)
            if stderr_stream is not None:
                result_stderr = read_stream(stderr_stream, stderr_cb, buffer_line=buffer_line)

            if result_stdout is None and result_stderr is None:
                break

        if stdout_stream is not None:
            read_stream(stdout_stream, stdout_cb, buffer_line=buffer_line, last=True)
        if stderr_stream is not None:
            read_stream(stderr_stream, stderr_cb, buffer_line=buffer_line, last=True)
        return 0

    with patch(obj, 'execute', execute):
        yield
