from collections import namedtuple
from contextlib import ExitStack, contextmanager
import os
import random
import sys
import unittest

from freezegun import freeze_time

from tests.execute_tests.helpers import textstream
from tests.helpers import check_pycolor_main
from tests.testutils import patch
from src.pycolor import __main__ as pycolor


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class PycolorTest(unittest.TestCase):
    def test_load_sample_config(self):
        curpath = os.path.dirname(os.path.realpath(__file__))
        with patch(
            pycolor, 'CONFIG_DIR', os.path.join(curpath, '../docs/sample-config')
        ), patch(
            pycolor, 'CONFIG_DEFAULT', os.path.join(curpath, '../docs/sample-config/rsync.json')
        ):
            try:
                pycolor.main(['--stdin', 'rsync'], stdin_stream=textstream())
            except SystemExit as sexc:
                self.assertEqual(sexc.code, 0)

    def test_version(self):
        stdout = textstream()
        with patch(sys, 'stdout', stdout):
            try:
                pycolor.main(['--version'])
            except SystemExit as sexc:
                if sexc.code != 0:
                    raise sexc

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
