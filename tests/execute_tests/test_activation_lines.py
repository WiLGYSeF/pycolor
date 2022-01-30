import os
import unittest

from tests.execute_tests.helpers import check_pycolor_execute

MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')

class ActivationLinesTest(unittest.TestCase):
    def test_activation_line(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'activation_line')

    def test_activation_line_list(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'activation_line_list')

    def test_activation_expression(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'activation_expression')

    def test_git_status(self):
        check_pycolor_execute(self, ['git', 'status'], MOCKED_DATA, 'git_status')
