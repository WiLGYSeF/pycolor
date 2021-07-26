import os
import unittest

from config import ConfigRegexError, ConfigExclusivePropertyError
from pycolor_class import Pycolor


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class ConfigTest(unittest.TestCase):
    def test_regex_exception(self):
        pycobj = Pycolor()
        with self.assertRaises(ConfigRegexError):
            self.load_file(pycobj, 'regex-exception')

    def test_mutual_exception(self):
        pycobj = Pycolor()
        with self.assertRaises(ConfigExclusivePropertyError):
            self.load_file(pycobj, 'mutual-exclusion-exception')

    def load_file(self, pycobj, name):
        pycobj.load_file(os.path.join(MOCKED_DATA, name + '.json'))
