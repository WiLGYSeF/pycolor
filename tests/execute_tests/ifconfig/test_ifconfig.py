import os
import unittest
import unittest.mock

from tests.execute_tests.helpers import check_pycolor_execute


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class IfconfigTest(unittest.TestCase):
    def test_super_expression(self):
        check_pycolor_execute(self, ['ifconfig'], MOCKED_DATA, 'super-expression')