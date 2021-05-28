from contextlib import contextmanager
import io
import os
import select
import sys

from tests.testutils import patch

import pycolor
import pycolor_class


def check_pycolor_execute(
    self,
    cmd,
    mocked_data_dir,
    test_name,
    **kwargs
):
    print_output = kwargs.get('print_output', False)
    write_output = kwargs.get('write_output', False)
    debug = kwargs.get('debug', 0)

    pycobj = create_pycolor_object(debug=debug)
    filename_prefix = os.path.join(mocked_data_dir, test_name)
    pycobj.load_file(filename_prefix + '.json')

    stdout = open_fstream(filename_prefix + '.txt')
    stderr = open_fstream(filename_prefix + '.err.txt')

    output_expected = read_file(filename_prefix + '.out.txt')
    output_expected_err = read_file(filename_prefix + '.out.err.txt')

    with execute_patch(pycolor_class.execute, stdout, stderr):
        pycobj.execute(cmd)

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

def check_pycolor_stdin(
    self,
    profile_name,
    mocked_data_dir,
    test_name,
    **kwargs
):
    print_output = kwargs.get('print_output', False)
    write_output = kwargs.get('write_output', False)
    debug = kwargs.get('debug', 0)

    pycobj = create_pycolor_object(debug=debug)
    filename_prefix = os.path.join(mocked_data_dir, test_name)
    pycobj.load_file(filename_prefix + '.json')

    stdin = io.TextIOWrapper(io.BytesIO(read_file(filename_prefix + '.txt')))
    output_expected = read_file(filename_prefix + '.out.txt')

    pycobj.set_current_profile(pycobj.get_profile_by_name(profile_name))
    pycolor.read_input_stream(pycobj, stdin)

    test_stream(self,
        pycobj.stdout,
        filename_prefix + '.out.txt',
        output_expected,
        print_output,
        write_output
    )

def test_stream(self, stream, fname, testdata, print_output, write_output):
    stream.seek(0)
    data = stream.buffer.read()

    if print_output: #pragma: no cover
        print(data.decode('utf-8'))
    if write_output: #pragma: no cover
        write_file(fname, data)

    if testdata is not None:
        self.assertEqual(data, testdata)
    else:
        self.assertEqual(data, b'')

def create_pycolor_object(debug=0):
    pycobj = pycolor_class.Pycolor(color_mode='always', debug=debug)
    pycobj.stdout = textstream()
    pycobj.stderr = textstream()
    return pycobj

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

                self.returncode = None
                self.polled = 0

            def poll(self):
                if self.polled > 1:
                    self.returncode = 0
                self.polled += 1

                return self.returncode

        return MockProcess(
            args,
            **kwargs
        )

    select_unpatched = select.select

    def _select(rlist, wlist, xlist, *args):
        timeout = args[0] if len(args) >= 1 else -1

        rkeys = []
        for key in rlist:
            if key is not sys.stdin:
                if isinstance(key, int) and key != -1:
                    fdlist = select_unpatched([key], [], [], 0.001)[0]
                    if len(fdlist) != 0:
                        rkeys.extend(fdlist)
                else:
                    rkeys.append(key)
        return (rkeys,)

    with patch(getattr(obj, 'subprocess'), 'Popen', popen),\
        patch(getattr(obj, 'select'), 'select', _select):
        yield

def textstream():
    return io.TextIOWrapper(io.BytesIO())

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

def write_file(fname, data): #pragma: no cover
    if len(data) == 0:
        return

    with open(fname, 'wb') as file:
        file.write(data)
        print('Wrote to ' + fname)
