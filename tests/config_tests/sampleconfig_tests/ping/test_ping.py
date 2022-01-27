import os
import typing
import unittest

from tests.config_tests.sampleconfig_tests.helpers import get_sample_config_filename
from tests.execute_tests.helpers import check_pycolor_execute

MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')

class PingTest(unittest.TestCase):
    def test_ping_local(self):
        _do_execute(self, ['ping', '-c', '5', '127.0.0.1'], 'ping_local')

    def test_ping_google(self):
        _do_execute(self, ['ping', '-c', '5', 'www.google.com'], 'ping_google')

    def test_ping_google_timestamp(self):
        _do_execute(self, ['ping', '-c', '3', '-D', 'www.google.com'], 'ping_google_timestamp')

    def test_ping_windows(self):
        _do_execute(self, ['ping', 'www.google.com'], 'ping_windows', config='ping-windows')

def _do_execute(self, args: typing.List[str], test_name: str, **kwargs) -> None:
    check_pycolor_execute(self,
        args,
        MOCKED_DATA,
        test_name,
        config_file=get_sample_config_filename(
            kwargs.get('config', 'ping-unix')
        ),
        profile_name='ping',
        **kwargs
    )
