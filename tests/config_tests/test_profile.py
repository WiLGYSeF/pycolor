import unittest

from config import ConfigPropertyError
import config.profile
from config.profile import Profile




class ProfileTest(unittest.TestCase):
    def test_profile_name_empty(self):
        prof = Profile({
            'profile_name': '',
        })
        self.assertIsNone(prof.profile_name)

    def test_min_max_args_fail(self):
        with self.assertRaises(ConfigPropertyError):
            Profile({
                'profile_name': 'test',
                'min_args': 4,
                'max_args': 2,
            })
