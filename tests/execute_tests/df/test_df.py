import os
import unittest
import unittest.mock

from tests.execute_tests.helpers import check_pycolor_execute, check_pycolor_stdin


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class DfTest(unittest.TestCase):
    def test_normal(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'normal')

    def test_color_fields(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'color-fields')

    def test_no_color_fields_T(self): #pylint: disable=invalid-name
        check_pycolor_execute(self, ['df', '-Th'], MOCKED_DATA, 'no-color-fields-T')
        check_pycolor_execute(self, ['df', '-h', '-T'], MOCKED_DATA, 'no-color-fields-T')

    def test_numbers_field(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'numbers-field')

    def test_color_fields_stdin(self):
        check_pycolor_stdin(self, 'df', MOCKED_DATA, 'color-fields')
