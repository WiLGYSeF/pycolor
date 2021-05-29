import os
import unittest

from tests.execute_tests.helpers import check_pycolor_execute


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class GitTest(unittest.TestCase):
    def test_status(self):
        check_pycolor_execute(self,
            ['git', 'status'],
            MOCKED_DATA,
            'status'
        )
