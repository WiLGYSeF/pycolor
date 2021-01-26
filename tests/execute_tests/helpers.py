from contextlib import contextmanager
import io
import os

from tests.testutils import patch

from execute import read_stream
import pycolor_class


def check_pycolor_execute(self, cmd, mocked_data_dir, test_name, print_output=False):
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
            with open(fname, 'r') as file:
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

    pycobj.stdout = io.TextIOWrapper(io.BytesIO())
    pycobj.stderr = io.TextIOWrapper(io.BytesIO())

    with execute_patch(pycolor_class.execute, stdout, stderr):
        pycobj.execute(cmd)

    if stdout is not None:
        stdout.close()
    if stderr is not None:
        stderr.close()

    if output_expected is not None:
        pycobj.stdout.seek(0)
        data = pycobj.stdout.read()
        if print_output:
            print(data)
        self.assertEqual(data, output_expected)

    if output_expected_err is not None:
        pycobj.stderr.seek(0)
        data = pycobj.stderr.read()
        if print_output:
            print(data)
        self.assertEqual(data, output_expected_err)

@contextmanager
def execute_patch(obj, stdout_stream, stderr_stream):
    def execute(cmd, stdout_callback, stderr_callback, buffer_line=True):
        while True:
            result_stdout = None
            result_stderr = None

            if stdout_stream is not None:
                result_stdout = read_stream(stdout_stream, stdout_callback, buffer_line=buffer_line)
            if stderr_stream is not None:
                result_stderr = read_stream(stderr_stream, stderr_callback, buffer_line=buffer_line)

            if result_stdout is None and result_stderr is None:
                break

        if stdout_stream is not None:
            read_stream(stdout_stream, stdout_callback, buffer_line=buffer_line, last=True)
        if stderr_stream is not None:
            read_stream(stderr_stream, stderr_callback, buffer_line=buffer_line, last=True)
        return 0

    with patch(obj, 'execute', execute):
        yield
