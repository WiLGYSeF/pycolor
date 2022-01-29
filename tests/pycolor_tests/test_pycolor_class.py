import sys
import unittest

from src.pycolor.config.profile import Profile
from src.pycolor.pycolor.pycolor_class import Pycolor
from tests.execute_tests.helpers import textstream
from tests.testutils import patch

class PycolorClassTest(unittest.TestCase):
    def test_color_mode_auto(self):
        pycobj = Pycolor(color_mode='always')
        self.assertEqual(pycobj.color_mode, 'always')
        self.assertTrue(pycobj.is_color_enabled)

    def test_current_profile(self):
        pycobj = Pycolor()
        self.assertIsNone(pycobj.current_profile)

        prof = Profile({})
        pycobj.current_profile = prof
        self.assertEqual(prof, pycobj.current_profile)

    def test_execute_file_not_found(self):
        pycobj = Pycolor()

        with patch(sys, 'stderr', textstream()),\
        self.assertRaises(SystemExit),\
        self.assertRaises(FileNotFoundError):
            pycobj.execute(['test_command_does_not_exist'])
