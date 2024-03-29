import os
import unittest

from src.pycolor.config import ConfigRegexError, ConfigExclusivePropertyError
from src.pycolor.pycolor.pycolor_class import Pycolor

MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')

class ConfigTest(unittest.TestCase):
    def test_regex_exception(self):
        pycobj = Pycolor()
        with self.assertRaises(ConfigRegexError):
            _load_file(pycobj, 'regex-exception')

    def test_mutual_exception(self):
        pycobj = Pycolor()
        with self.assertRaises(ConfigExclusivePropertyError):
            _load_file(pycobj, 'mutual-exclusion-exception')

    def test_replace_fields_nonzero_field(self):
        pycobj = Pycolor()
        with self.assertRaises(ConfigExclusivePropertyError):
            _load_file(pycobj, 'replace-fields-nonzero-field')

def _load_file(pycobj, name):
    pycobj.load_file(os.path.join(MOCKED_DATA, name + '.json'))
    for prof in pycobj.profiles:
        prof.load_patterns()
