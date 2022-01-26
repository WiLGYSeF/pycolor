import os
import sys
import unittest

from freezegun import freeze_time

from tests.execute_tests.helpers import textstream
from tests.helpers import check_pycolor_main
from tests.testutils import patch
from src.pycolor import __main__ as pycolor

CURPATH = os.path.dirname(os.path.realpath(__file__))
MOCKED_DATA = os.path.join(CURPATH, 'mocked_data')
SAMPLE_CONFIG_DIR = os.path.join(CURPATH, '../../src/pycolor/config/sample-config')

class PycolorTest(unittest.TestCase):
    def test_load_sample_config(self):
        self.assertTrue(os.path.isdir(SAMPLE_CONFIG_DIR))

        with patch(pycolor, 'CONFIG_DIR', SAMPLE_CONFIG_DIR),\
        patch(pycolor, 'CONFIG_DEFAULT', os.path.join(SAMPLE_CONFIG_DIR, 'rsync.json')):
            stdin = textstream()
            with open(os.path.join(MOCKED_DATA, 'load_sample_config.txt'), 'r') as file:
                stdin.write(file.read())
                stdin.seek(0)

            check_pycolor_main(self,
                ['--stdin', 'rsync'],
                MOCKED_DATA,
                'load_sample_config',
                stdin=stdin,
                no_load_args=True
            )

    def test_version(self):
        stdout = textstream()
        with patch(sys, 'stdout', stdout):
            check_pycolor_main(self, ['--version'], MOCKED_DATA, 'version')

        stdout.seek(0)
        self.assertEqual(stdout.read(), pycolor.__version__ + '\n')

    def test_ls_numbers(self):
        check_pycolor_main(self, ['ls', '-l'], MOCKED_DATA, 'ls_numbers')

    def test_ls_numbers_known_arg_parse(self):
        check_pycolor_main(self, ['ls', '-l', '--color', 'off'], MOCKED_DATA, 'ls_numbers')

    @freeze_time('2000-01-02 03:45:56')
    def test_ls_timestamp_arg(self):
        check_pycolor_main(self, ['--timestamp', '--', 'ls', '-l'], MOCKED_DATA, 'ls_timestamp_arg')

    @freeze_time('2000-01-02 03:45:56')
    def test_ls_timestamp_arg_default_profile(self):
        check_pycolor_main(self,
            ['--timestamp', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_timestamp_arg_default_profile'
        )

    def test_ls_profile_named(self):
        check_pycolor_main(self,
            ['--profile', 'num', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_profile_named'
        )

    def test_ls_profile_none(self):
        check_pycolor_main(self,
            ['--no-execv', '--profile=', '--', 'ls', '-l'],
            MOCKED_DATA,
            'ls_profile_none'
        )

    def test_ls_stdin(self):
        name = 'ls_stdin'
        with open(os.path.join(MOCKED_DATA, name + '.txt'), 'r') as stdin:
            check_pycolor_main(self,
                ['--stdin', 'ls', '-l'],
                MOCKED_DATA,
                name,
                stdin=stdin
            )

    def test_df_color_alias(self):
        check_pycolor_main(self,
            ['df', '-h'],
            MOCKED_DATA,
            'df_color_alias'
        )

    def test_ls_profile_fail(self):
        with self.assertRaises(SystemExit), patch(pycolor, 'printerr', lambda x: None):
            check_pycolor_main(self,
                ['--profile', 'invalid', '--', 'ls', '-l'],
                MOCKED_DATA,
                'ls_profile_named'
            )

    def test_unknown_command(self):
        with self.assertRaises(SystemExit):
            check_pycolor_main(self,
                ['this-is-not-a-valid-command-peucrnh'],
                MOCKED_DATA,
                'unknown_command',
                patch_stderr=True
            )

    def test_from_profile_not_exist(self):
        with self.assertRaises(SystemExit):
            check_pycolor_main(self,
                ['-p=test', 'ls', '-l'],
                MOCKED_DATA,
                'from_profile_not_exist',
                patch_stderr=True
            )

    def test_free_tty(self):
        check_pycolor_main(self,
            ['free', '-h'],
            MOCKED_DATA,
            'free_tty'
        )

    def test_stdin_no_profile_no_cmd_args(self):
        with self.assertRaises(SystemExit):
            check_pycolor_main(self,
                [],
                MOCKED_DATA,
                'stdin_no_profile_no_cmd_args',
                patch_stdout=True
            )
