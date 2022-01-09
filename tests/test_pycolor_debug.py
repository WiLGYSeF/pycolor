from collections import namedtuple
from contextlib import contextmanager
import os
import random
import unittest

from freezegun import freeze_time

from tests.helpers import check_pycolor_main
from tests.testutils import patch
from src.pycolor import __main__ as pycolor

MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')

class PycolorTest(unittest.TestCase):
    def test_debug_color(self):
        #pylint: disable=invalid-name
        def get_terminal_size(fd=None):
            TerminalSize = namedtuple('terminal_size', ['columns', 'lines'])
            return TerminalSize(80, 24)

        with patch(os, 'get_terminal_size', get_terminal_size):
            check_pycolor_main(self,
                ['--debug-color'],
                MOCKED_DATA,
                'debug_color',
                patch_stdout=True
            )

    def test_debug_format(self):
        check_pycolor_main(self,
            [
                '--debug-format',
                'this %C(lr)is %C(und;ly)a %C(^und;bol;bli;g)test'
            ],
            MOCKED_DATA,
            'debug_format',
            patch_stdout=True
        )

    def test_debug_format_short(self):
        check_pycolor_main(self,
            [
                '-f',
                'this %C(lr)is %C(und;ly)a %C(^und;bol;bli;g)test'
            ],
            MOCKED_DATA,
            'debug_format_short',
            patch_stdout=True
        )

    def test_ls_debug_v1(self):
        check_pycolor_main(self,
            ['-v', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_debug_v1',
            patch_stdout=True
        )

    def test_ls_debug_v1_no_color(self):
        check_pycolor_main(self,
            ['-v', '--color=off', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_debug_v1_no_color',
            patch_stdout=True
        )

    def test_ls_debug_v2(self):
        check_pycolor_main(self,
            ['-vv', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_debug_v2',
            patch_stdout=True
        )

    def test_ls_debug_v3(self):
        check_pycolor_main(self,
            ['-vvv', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_debug_v3',
            patch_stdout=True
        )

    @freeze_time('2000-01-02 03:45:56')
    def test_debug_file(self):
        test_name = 'debug_file'
        with self.check_debug_log(MOCKED_DATA, test_name) as fname:
            check_pycolor_main(self, ['--debug-log', fname, 'free', '-h'], MOCKED_DATA, test_name)

    @freeze_time('2000-01-02 03:45:56')
    def test_debug_file_v3(self):
        test_name = 'debug_file_v3'
        with self.check_debug_log(MOCKED_DATA, test_name) as fname:
            check_pycolor_main(self,
                ['-vvv', '--debug-log', fname, 'free', '-h'],
                MOCKED_DATA,
                test_name
            )

    @freeze_time('2000-01-02 03:45:56')
    def test_debug_file_out(self):
        test_name = 'debug_file_out'
        with self.check_debug_log(MOCKED_DATA, test_name) as fname:
            check_pycolor_main(self,
                ['--debug-log-out', fname, 'free', '-h'],
                MOCKED_DATA,
                test_name,
                patch_stdout=True
            )

    @contextmanager
    def check_debug_log(self, mocked_data_dir, test_name, **kwargs):
        print_output = kwargs.get('print_output', False)
        write_output = kwargs.get('write_output', False)

        fname = random_tmp_filename()
        yield fname

        try:
            debug_fname = os.path.join(mocked_data_dir, test_name) + '.out.debug.txt'

            with open(fname, 'r') as file:
                filedata = file.read()
                if print_output: #pragma: no cover
                    print(filedata)

                if write_output: #pragma: no cover
                    with open(debug_fname, 'w') as debugfile:
                        debugfile.write(filedata)
                else:
                    with open(debug_fname, 'r') as debugfile:
                        self.assertEqual(debugfile.read(), filedata)
        finally:
            os.remove(fname)

def random_tmp_filename():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    length = 8

    fname = 'tmp-'
    for _ in range(length):
        fname += chars[random.randint(0, len(chars) - 1)]
    return fname
