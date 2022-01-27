import os
import typing
import unittest

from tests.config_tests.sampleconfig_tests.helpers import get_sample_config_filename
from tests.execute_tests.helpers import check_pycolor_execute

MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')

class DfTest(unittest.TestCase):
    def test_df(self):
        _do_execute(self, ['df', '-h'], 'df')

    def test_df_T(self): # pylint: disable=invalid-name
        _do_execute(self, ['df', '-Th'], 'df_T')
        _do_execute(self, ['df', '-h', '-T'], 'df_T')

    def test_df_output(self):
        _do_execute(self, ['df', '-h', '--output=source,used'], 'output')

    def test_df_total(self):
        _do_execute(self, ['df', '-h', '--total'], 'total')

def _do_execute(self, args: typing.List[str], test_name: str, **kwargs) -> None:
    check_pycolor_execute(self,
        args,
        MOCKED_DATA,
        test_name,
        config_file=get_sample_config_filename('df'),
        **kwargs
    )
