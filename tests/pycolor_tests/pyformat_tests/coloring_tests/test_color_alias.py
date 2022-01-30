import os
import unittest

from tests.helpers import check_pycolor_main

CURPATH = os.path.dirname(os.path.realpath(__file__))
MOCKED_DATA = os.path.join(CURPATH, 'mocked_data')

class ColorAliasTest(unittest.TestCase):
    def test_df_color_alias(self):
        check_pycolor_main(self,
            ['df', '-h'],
            MOCKED_DATA,
            'df_color_alias'
        )
