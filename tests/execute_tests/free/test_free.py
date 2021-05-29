import os
import unittest

from tests.execute_tests.helpers import check_pycolor_execute


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class FreeTest(unittest.TestCase):
    def test_color(self):
        check_pycolor_execute(self, ['free'], MOCKED_DATA, 'color')

    def test_color_human(self):
        check_pycolor_execute(self, ['free', '-h'], MOCKED_DATA, 'color-human')

    def test_color_count(self):
        check_pycolor_execute(self, ['free', '-c4'], MOCKED_DATA, 'color-count')

    def test_color_replace_fields(self):
        check_pycolor_execute(self, ['free', '-h'], MOCKED_DATA, 'color-replace-fields')

    def test_color_replace_fields_list(self):
        check_pycolor_execute(self, ['free', '-h'], MOCKED_DATA, 'color-replace-fields-list')

    def test_replace_fields_all(self):
        check_pycolor_execute(self, ['free', '-h'], MOCKED_DATA, 'replace-fields-all')

    def test_replace_groups_all(self):
        check_pycolor_execute(self, ['free', '-h'], MOCKED_DATA, 'replace-groups-all')
