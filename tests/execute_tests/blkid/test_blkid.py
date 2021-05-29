import os
import unittest

from tests.execute_tests.helpers import check_pycolor_execute


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class BlkidTest(unittest.TestCase):
    def test_replace_groups_list(self):
        check_pycolor_execute(self, ['blkid'], MOCKED_DATA, 'replace-groups-list')

    def test_replace_groups_list_overlap_before(self):
        check_pycolor_execute(self, ['blkid'], MOCKED_DATA, 'replace-groups-list-overlap-before')

    def test_replace_groups_list_overlap_after(self):
        check_pycolor_execute(self, ['blkid'], MOCKED_DATA, 'replace-groups-list-overlap-after')

    def test_replace_groups_list_overlap_before_prev(self):
        check_pycolor_execute(self,
            ['blkid'],
            MOCKED_DATA,
            'replace-groups-list-overlap-before-prev'
        )

    def test_replace_groups_list_overlap_after_prev(self):
        check_pycolor_execute(self,
            ['blkid'],
            MOCKED_DATA,
            'replace-groups-list-overlap-after-prev'
        )
