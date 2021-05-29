import os
import unittest

from tests.execute_tests.helpers import check_pycolor_execute


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class LsTest(unittest.TestCase):
    def test_normal(self):
        check_pycolor_execute(self, ['ls', '-l'], MOCKED_DATA, 'normal')

    def test_normal_color(self):
        check_pycolor_execute(self, ['ls', '-l'], MOCKED_DATA, 'normal-color')

    def test_yellow_executable(self):
        check_pycolor_execute(self, ['ls', '-l'], MOCKED_DATA, 'yellow-executable')

    def test_numbers_from_profile(self):
        check_pycolor_execute(self, ['ls', '-l'], MOCKED_DATA, 'numbers-from-profile')

    def test_numbers_from_profile_str(self):
        check_pycolor_execute(self, ['ls', '-l'], MOCKED_DATA, 'numbers-from-profile-str')

    def test_numbers_from_profile_list_str(self):
        check_pycolor_execute(self, ['ls', '-l'], MOCKED_DATA, 'numbers-from-profile-list-str')

    def test_filter_py(self):
        check_pycolor_execute(self, ['ls', '-l'], MOCKED_DATA, 'filter-py')

    def test_filter_field_py(self):
        check_pycolor_execute(self, ['ls', '-l'], MOCKED_DATA, 'filter-field-py')

    def test_yellow_executable_soft_reset(self):
        check_pycolor_execute(self, ['ls', '-l'], MOCKED_DATA, 'yellow-executable-soft-reset')

    def test_yellow_executable_replace_groups(self):
        check_pycolor_execute(self, ['ls', '-l'], MOCKED_DATA, 'yellow-executable-replace-groups')

    def test_yellow_executable_replace_groups_list(self):
        check_pycolor_execute(self,
            ['ls', '-l'],
            MOCKED_DATA,
            'yellow-executable-replace-groups-list'
        )
