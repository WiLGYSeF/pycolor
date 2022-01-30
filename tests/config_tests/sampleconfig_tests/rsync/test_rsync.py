import os
import typing
import unittest

from tests.config_tests.sampleconfig_tests.helpers import get_sample_config_filename
from tests.execute_tests.helpers import check_pycolor_execute

MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')

class RsyncTest(unittest.TestCase):
    def test_rsync(self):
        _do_execute(self,
            ['rsync', '-auvzn', '--delete', 'src/pycolor', 'tests', 'tmp'],
            'rsync'
        )

def _do_execute(self, args: typing.List[str], test_name: str, **kwargs) -> None:
    check_pycolor_execute(self,
        args,
        MOCKED_DATA,
        test_name,
        config_file=get_sample_config_filename('rsync'),
        **kwargs
    )
