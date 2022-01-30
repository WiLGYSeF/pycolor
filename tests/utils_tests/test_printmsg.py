from contextlib import contextmanager
import typing
import unittest

from src.pycolor.utils import printmsg as pkg_printmsg
from src.pycolor.utils.printmsg import printmsg, printerr, printwarn, is_color_enabled
from tests.testutils import patch, patch_stderr

class PrintmsgTest(unittest.TestCase):
    def test_printmsg_filename(self):
        self.assertPrintmsg(
            lambda: printmsg('test', filename='file'),
            '\x1b[93mfile\x1b[0m: test\n',
            'file: test\n'
        )

    def test_printerr(self):
        self.assertPrintmsg(
            lambda: printerr('test'),
            '\x1b[91merror\x1b[0m: test\n',
            'error: test\n'
        )

    def test_printwarn(self):
        self.assertPrintmsg(
            lambda: printwarn('test'),
            '\x1b[93mwarn\x1b[0m: test\n',
            'warn: test\n'
        )

    def test_is_color_enabled(self):
        entries = [
            ('always', True),
            ('on', True),
            ('1', True),
            ('never', False),
            ('off', False),
            ('0', False),
        ]

        for entry in entries:
            color = entry[0]
            with self.subTest(color=color):
                self.assertEqual(entry[1], is_color_enabled(color))

    def assertPrintmsg(self,
        func: typing.Callable,
        expected_color: str,
        expected_nocolor: str
    ) -> None:
        with self.subTest(expected=expected_color):
            with patch_color(True), patch_stderr() as stream:
                func()
                stream.seek(0)
                self.assertEqual(expected_color, stream.read())
        with self.subTest(expected=expected_nocolor):
            with patch_color(False), patch_stderr() as stream:
                func()
                stream.seek(0)
                self.assertEqual(expected_nocolor, stream.read())

@contextmanager
def patch_color(enabled: bool):
    with patch(pkg_printmsg, 'is_color_enabled', lambda x: enabled):
        yield
