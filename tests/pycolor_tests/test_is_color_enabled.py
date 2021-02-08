import unittest

import pycolor_class


IS_COLOR_ENABLED = {
    'always': True,
    'on': True,
    '1': True,
    'never': False,
    'off': False,
    '0': False,
}


class IsColorEnabledTest(unittest.TestCase):
    def test_is_color_enabled(self):
        for key, val in IS_COLOR_ENABLED.items():
            pycobj = pycolor_class.Pycolor(color_mode=key)
            self.assertEqual(pycobj.is_color_enabled(), val)
