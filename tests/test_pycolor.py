from contextlib import ExitStack, contextmanager
import os
import random
import sys
import unittest

from freezegun import freeze_time

from tests.execute_tests.helpers import (
    execute_patch, open_fstream, read_file, test_stream, textstream
)
from tests.testutils import patch
import pycolor
import pycolor_class


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class PycolorTest(unittest.TestCase):
    def test_main_ls_numbers(self):
        self.check_pycolor_main(['ls', '-l'], MOCKED_DATA, 'ls_numbers')

    def test_main_ls_numbers_known_arg_parse(self):
        self.check_pycolor_main(['ls', '-l', '--color', 'off'], MOCKED_DATA, 'ls_numbers')

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

    def test_main_ls_profile_named(self):
        self.check_pycolor_main(
            ['--profile', 'num', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_profile_named'
        )

    def test_main_ls_profile_none(self):
        self.check_pycolor_main(
            ['--no-execv', '--profile=', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_profile_none'
        )

    def test_main_debug_color(self):
        self.check_pycolor_main(['--debug-color'], MOCKED_DATA, 'debug_color', patch_stdout=True)

    def test_main_debug_format(self):
        self.check_pycolor_main([
            '--debug-format', 'this %C(lr)is %C(und;ly)a %C(^und;bol;bli;g)test'
        ], MOCKED_DATA, 'debug_format', patch_stdout=True)

    def test_main_ls_profile_fail(self):
        with self.assertRaises(SystemExit), patch(pycolor, 'printerr', lambda x: None):
            self.check_pycolor_main(
                ['--profile', 'invalid', '--', 'ls', '-l'],
                MOCKED_DATA,
                'ls_profile_named'
            )

    def test_free_tty(self):
        self.check_pycolor_main(
            ['free', '-h'],
            MOCKED_DATA,
            'free_tty'
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

    def test_main_ls_debug_v2(self):
        self.check_pycolor_main(
            ['-vv', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_debug_v2',
            patch_stdout=True
        )

    def test_main_ls_debug_v3(self):
        self.check_pycolor_main(
            ['-vvv', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_debug_v3',
            patch_stdout=True
        )

    @freeze_time('2000-01-02 03:45:56')
    def test_debug_file(self):
        test_name = 'debug_file'
        with self.check_debug_log(MOCKED_DATA, test_name) as fname:
            self.check_pycolor_main(['--debug-log', fname, 'free', '-h'], MOCKED_DATA, test_name)

    @freeze_time('2000-01-02 03:45:56')
    def test_debug_file_v3(self):
        test_name = 'debug_file_v3'
        with self.check_debug_log(MOCKED_DATA, test_name) as fname:
            self.check_pycolor_main(
                ['-vvv', '--debug-log', fname, 'free', '-h'],
                MOCKED_DATA,
                test_name
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
        stdout = textstream()
        stderr = textstream()

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

    @contextmanager
    def check_debug_log(self, mocked_data_dir, test_name, **kwargs):
        print_output = kwargs.get('print_output', False)
        write_output = kwargs.get('write_output', False)

        try:
            fname = random_tmp_filename()
            yield fname
        finally:
            try:
                debug_fname = os.path.join(mocked_data_dir, test_name) + '.out.debug.txt'

                with open(fname, 'r') as file:
                    filedata = file.read()
                    if print_output: #pragma: no cover
                        print(filedata)

                    if write_output:
                        #pragma: no cover
                        with open(debug_fname, 'w') as debugfile:
                            debugfile.write(filedata)
                    else:
                        with open(debug_fname, 'r') as debugfile:
                            self.assertEqual(filedata, debugfile.read())
            finally:
                os.remove(fname)

def random_tmp_filename():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    length = 8

    fname = 'tmp'
    for _ in range(length):
        fname += chars[random.randint(0, len(chars) - 1)]
    return fname
