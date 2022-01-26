import os
import unittest

from freezegun import freeze_time

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

    def test_color_fields_activation_line(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'color-fields-activation-line')

    def test_color_fields_activation_line_list(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'color-fields-activation-line-list')

    @freeze_time('1997-01-31 12:34:56')
    def test_timestamp(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'timestamp')

    def test_color_fields_list(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'color-fields-list')

    def test_color_fields_pad(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'color-fields-pad')

    def test_table(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'table')

    def test_field_replace(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'field-replace')

    def test_field_replace_groups(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'field-replace-groups')
