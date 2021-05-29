import os
import unittest

from tests.execute_tests.helpers import check_pycolor_execute


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class RsyncTest(unittest.TestCase):
    def test_groups_star(self):
        check_pycolor_execute(self,
            ['rsync', '-auvzPh', 'video.mp4'],
            MOCKED_DATA,
            'groups-star'
        )

    def test_groups_nums(self):
        check_pycolor_execute(self,
            ['rsync', '-auvzPh', 'video.mp4'],
            MOCKED_DATA,
            'groups-nums'
        )
