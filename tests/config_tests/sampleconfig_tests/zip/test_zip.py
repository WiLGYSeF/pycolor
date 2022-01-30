import os
import typing
import unittest

from tests.config_tests.sampleconfig_tests.helpers import get_sample_config_filename
from tests.execute_tests.helpers import check_pycolor_execute

MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')

class ZipTest(unittest.TestCase):
    def test_zip(self):
        _do_execute(self,
            ['zip', '-r', 'abc.zip', 'src/pycolor', 'tests'],
            'zip'
        )

    def test_zip_file_sync(self):
        _do_execute(self,
            ['zip', '-r', '-FS', 'abc.zip', 'src/pycolor', 'tests'],
            'zip_file_sync'
        )

    def test_zip_file_sync_db_dc(self):
        _do_execute(self,
            ['zip', '-r', '-db', '-dc', '-FS', 'abc.zip', 'src/pycolor', 'tests'],
            'zip_file_sync_db_dc'
        )

def _do_execute(self, args: typing.List[str], test_name: str, **kwargs) -> None:
    check_pycolor_execute(self,
        args,
        MOCKED_DATA,
        test_name,
        config_file=get_sample_config_filename('zip'),
        **kwargs
    )
