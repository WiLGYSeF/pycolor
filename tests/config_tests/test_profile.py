import unittest

from config import ConfigPropertyException
import config.profile
from config.profile import Profile




class ProfileTest(unittest.TestCase):
    def test_min_max_args_fail(self):
        with self.assertRaises(ConfigPropertyException):
            Profile({
                'profile_name': 'test',
                'min_args': 4,
                'max_args': 2,
            })
