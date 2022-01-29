import os
import sys
import tempfile
import unittest

from tests.helpers import check_pycolor_main
from tests.testutils import patch, patch_stderr, textstream
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

    def test_copy_sample_config(self):
        self.assertTrue(os.path.isdir(SAMPLE_CONFIG_DIR))

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpconfig = os.path.join(tmpdir, 'config')
            with patch(sys, 'stdout', textstream()), patch(pycolor, 'CONFIG_DIR', tmpconfig):
                check_pycolor_main(self,
                    ['--version'],
                    MOCKED_DATA,
                    'empty',
                    patch_sample_config_dir=False
                )
                self.assertListEqual(
                    sorted(os.listdir(SAMPLE_CONFIG_DIR)),
                    sorted(os.listdir(tmpconfig))
                )

    def test_stdin_config_invalid_json(self):
        with patch_stderr() as stream:
            stdin = textstream()
            check_pycolor_main(self,
                ['--stdin', 'rsync'],
                MOCKED_DATA,
                'invalid_json',
                stdin=stdin
            )

            stream.seek(0)
            result = stream.read()
            self.assertTrue(
                result.startswith('\x1b[91merror\x1b[0m: \x1b[93m%s\x1b[0m: ' % (
                    os.path.join(MOCKED_DATA, 'invalid_json.json')
                ))
            )

    def test_stdin_config_invalid_profile(self):
        with patch_stderr() as stream:
            stdin = textstream()
            check_pycolor_main(self,
                ['--stdin', 'rsync'],
                MOCKED_DATA,
                'invalid_profile',
                stdin=stdin
            )

            stream.seek(0)
            result = stream.read()
            self.assertTrue(
                result.startswith('\x1b[91merror\x1b[0m: \x1b[93m%s\x1b[0m: ' % (
                    os.path.join(MOCKED_DATA, 'invalid_profile.json')
                ))
            )

    def test_stdin_config_invalid_pattern(self):
        with patch_stderr() as stream:
            stdin = textstream()
            with self.assertRaises(SystemExit):
                check_pycolor_main(self,
                    ['--stdin', 'rsync'],
                    MOCKED_DATA,
                    'invalid_pattern',
                    stdin=stdin
                )

            stream.seek(0)
            result = stream.read()
            self.assertEqual(
                result,
                '\x1b[91merror\x1b[0m: "expression": regex nothing to repeat at position 0\n'
            )
