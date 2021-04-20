import os
import unittest
import unittest.mock

from tests.execute_tests.helpers import check_pycolor_execute


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class BlkidTest(unittest.TestCase):
    def test_replace_groups_list(self):
        check_pycolor_execute(self, ['blkid'], MOCKED_DATA, 'replace-groups-list')
