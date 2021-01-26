import os
import unittest
import unittest.mock

from tests.execute_tests.helpers import execute_patch

import pycolor_class


MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class LsTest(unittest.TestCase):
    def test_normal(self):
        pycobj = pycolor_class.Pycolor()
        pycobj.load_file(os.path.join(MOCKED_DATA, 'normal') + '.json')

        try:
            stdout = open(os.path.join(MOCKED_DATA, 'normal.txt'), 'rb')
        except FileNotFoundError:
            stdout = None

        try:
            stderr = open(os.path.join(MOCKED_DATA, 'normal.err.txt'), 'rb')
        except FileNotFoundError:
            stderr = None

        try:
            with open(os.path.join(MOCKED_DATA, 'normal.out.txt'), 'rb') as file:
                output_expected = file.read()
        except FileNotFoundError:
            output_expected = None

        try:
            with open(os.path.join(MOCKED_DATA, 'normal.out.err.txt'), 'rb') as file:
                output_expected_err = file.read()
        except FileNotFoundError:
            output_expected_err = None

        if output_expected is None and output_expected_err is None:
            raise FileNotFoundError(
                '%s is missing expected output test files for: %s' % (MOCKED_DATA, 'normal')
            )

        output = b''
        output_err = b''

        def stdout_cb(data):
            nonlocal output
            print('s', data)
            output += data

        def stderr_cb(data):
            nonlocal output_err
            print('e', data)
            output_err += data

        with execute_patch(pycolor_class.execute, stdout, stderr, stdout_cb, stderr_cb):
            pycobj.execute('ls')

        if stdout is not None:
            stdout.close()
        if stderr is not None:
            stderr.close()

        if output_expected is not None:
            self.assertEqual(output, output_expected)
        if output_expected_err is not None:
            self.assertEqual(output_err, output_expected_err)
