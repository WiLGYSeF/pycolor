import os
import unittest
import unittest.mock

from tests.execute_tests.helpers import check_pycolor_execute


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class PylintTest(unittest.TestCase):
    def test_pylint(self):
        check_pycolor_execute(self,
            ['pylint', 'pycolor_class.py', 'execute.py'],
            MOCKED_DATA,
            'pylint'
        )

    def test_input_color(self):
        check_pycolor_execute(self,
            ['pylint', 'execute.py'],
            MOCKED_DATA,
            'input-color'
        )

    def test_remove_input_color(self):
        check_pycolor_execute(self,
            ['pylint', 'execute.py'],
            MOCKED_DATA,
            'remove-input-color'
        )
