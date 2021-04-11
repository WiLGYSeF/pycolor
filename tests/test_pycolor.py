from contextlib import ExitStack
import io
import os
import sys
import unittest

from freezegun import freeze_time

from tests.execute_tests.helpers import execute_patch, open_fstream, read_file, test_stream
from tests.testutils import patch
import pycolor
import pycolor_class


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')

ARGS = 'args'
SUBSET = 'subset'
RESULT = 'result'

CONSECUTIVE_END_ARGS = [
    {
        ARGS: [],
        SUBSET: [],
        RESULT: True
    },
    {
        ARGS: ['--color', 'on', 'abc'],
        SUBSET: [],
        RESULT: True
    },
    {
        ARGS: ['abc'],
        SUBSET: ['abc'],
        RESULT: True
    },
    {
        ARGS: ['--color', 'on', 'abc'],
        SUBSET: ['abc'],
        RESULT: True
    },
    {
        ARGS: ['--', 'asdf', '--color', 'on', 'abc'],
        SUBSET: ['asdf', '--color', 'on', 'abc'],
        RESULT: True
    },
    {
        ARGS: ['asdf', '--color', 'on', 'abc'],
        SUBSET: ['asdf', 'abc'],
        RESULT: False
    },
    {
        ARGS: ['asdf', 'abc', '--color', 'on'],
        SUBSET: ['asdf', 'abc'],
        RESULT: False
    },
    {
        ARGS: ['asdf', 'abc', '--color', 'on'],
        SUBSET: ['nowhere'],
        RESULT: False
    },
    {
        ARGS: ['asdf', 'abc', '--color', 'on'],
        SUBSET: ['abc'],
        RESULT: False
    },
    {
        ARGS: ['ee', 'asdf', 'abc'],
        SUBSET: ['asdf', 'abc', '123', '4'],
        RESULT: False
    },
]


class PycolorTest(unittest.TestCase):
    def test_main_ls_numbers(self):
        self.check_pycolor_main(['--', 'ls', '-l'], MOCKED_DATA, 'ls_numbers')

    def test_main_ls_numbers_with_dashdash(self):
        self.check_pycolor_main(['--', 'ls', '-l'], MOCKED_DATA, 'ls_numbers')

    def test_main_invalid_consecutive_args(self):
        with self.assertRaises(SystemExit):
            self.check_pycolor_main(['ls', '-l', '--color', 'on'], MOCKED_DATA, 'ls_numbers')

    def test_main_no_profile_stdin(self):
        with self.assertRaises(SystemExit), patch(pycolor, 'printerr', lambda x: None):
            self.check_pycolor_main([], MOCKED_DATA, 'ls_numbers')

    @freeze_time('2000-01-02 03:45:56')
    def test_main_ls_timestamp_arg(self):
        self.check_pycolor_main(['--timestamp', '--', 'ls', '-l'], MOCKED_DATA, 'ls_timestamp_arg')

    @freeze_time('2000-01-02 03:45:56')
    def test_main_ls_timestamp_arg_default_profile(self):
        self.check_pycolor_main(
            ['--timestamp', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_timestamp_arg_default_profile'
        )

    def test_main_ls_profile(self):
        self.check_pycolor_main(['--profile', 'none', '--', 'ls', '-l'], MOCKED_DATA, 'ls_profile')

    def test_main_ls_profile_fail(self):
        with self.assertRaises(SystemExit), patch(pycolor, 'printerr', lambda x: None):
            self.check_pycolor_main(
                ['--profile', 'invalid', '--', 'ls', '-l'],
                MOCKED_DATA,
                'ls_profile'
            )

    def test_main_ls_debug_v1(self):
        self.check_pycolor_main(
            ['-v', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_debug_v1',
            patch_stdout=True
        )

    def test_main_ls_debug_v1_no_color(self):
        self.check_pycolor_main(
            ['-v', '--color=off', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_debug_v1_no_color',
            patch_stdout=True
        )

    def test_consecutive_end_args(self):
        for entry in CONSECUTIVE_END_ARGS:
            self.assertEqual(
                pycolor.consecutive_end_args(entry[ARGS], entry[SUBSET]),
                entry[RESULT]
            )

    def check_pycolor_main(self,
        args,
        mocked_data_dir,
        test_name,
        **kwargs
    ):
        patch_stdout = kwargs.get('patch_stdout', False)
        print_output = kwargs.get('print_output', False)
        write_output = kwargs.get('write_output', False)

        filename_prefix = os.path.join(mocked_data_dir, test_name)
        stdout = io.TextIOWrapper(io.BytesIO())
        stderr = io.TextIOWrapper(io.BytesIO())

        args = ['--load-file', filename_prefix + '.json', '--color', 'always'] + args

        stdout_in = open_fstream(filename_prefix + '.txt')
        stderr_in = open_fstream(filename_prefix + '.err.txt')

        with ExitStack() as stack:
            stack.enter_context(execute_patch(pycolor_class.execute, stdout_in, stderr_in))
            if patch_stdout:
                stack.enter_context(patch(sys, 'stdout', stdout))

            try:
                pycolor.main(args, stdout_stream=stdout, stderr_stream=stderr)
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
