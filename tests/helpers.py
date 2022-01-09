from contextlib import ExitStack
import os
import sys

from tests.execute_tests.helpers import (
    execute_patch, open_fstream, read_file, test_stream, textstream
)
from tests.testutils import patch
from src.pycolor.pycolor import pycolor_class
from src.pycolor import __main__ as pycolor

def check_pycolor_main(self,
    args,
    mocked_data_dir,
    test_name,
    **kwargs
):
    stdin = kwargs.get('stdin', sys.stdin)
    patch_stdout = kwargs.get('patch_stdout', False)
    patch_stderr = kwargs.get('patch_stderr', False)
    print_output = kwargs.get('print_output', False)
    write_output = kwargs.get('write_output', False)

    filename_prefix = os.path.join(mocked_data_dir, test_name)
    stdout = textstream()
    stderr = textstream()

    args = ['--load-file', filename_prefix + '.json', '--color', 'always'] + args

    stdout_in = open_fstream(filename_prefix + '.txt')
    stderr_in = open_fstream(filename_prefix + '.err.txt')

    with ExitStack() as stack:
        stack.enter_context(execute_patch(pycolor_class.execute, stdout_in, stderr_in))
        if patch_stdout:
            stack.enter_context(patch(sys, 'stdout', stdout))
        if patch_stderr:
            stack.enter_context(patch(sys, 'stderr', stderr))

        try:
            pycolor.main(args, stdout_stream=stdout, stderr_stream=stderr, stdin_stream=stdin)
        except SystemExit as sexc:
            if sexc.code != 0:
                raise sexc
        finally:
            if stdout_in is not None:
                stdout_in.close()
            if stderr_in is not None:
                stderr_in.close()

    output_expected = read_file(filename_prefix + '.out.txt')
    output_expected_err = read_file(filename_prefix + '.out.err.txt')

    test_stream(self,
        stdout,
        filename_prefix + '.out.txt',
        output_expected,
        print_output,
        write_output
    )
    test_stream(self,
        stderr,
        filename_prefix + '.out.err.txt',
        output_expected_err,
        print_output,
        write_output
    )
