import os
import sys
import tempfile
import unittest

from src.pycolor.config.profile import Profile
from src.pycolor.pycolor.pycolor_class import Pycolor

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
