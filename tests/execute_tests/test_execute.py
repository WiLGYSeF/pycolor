import datetime
import io
import os
import unittest

from freezegun import freeze_time

from src.pycolor.execute import execute
from tests.execute_tests.helpers import check_pycolor_execute
from tests.testutils import textstream

MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')

class ExecuteTest(unittest.TestCase):
    def test_execute_cat(self):
        stdin = textstream()
        expected = 'this is a test'
        output = ''
        received_err = False

        stdin.write(expected)
        stdin.seek(0)

        def stdout_cb(data):
            nonlocal output
            output += data

        def stderr_cb(data):
            nonlocal received_err
            received_err = True

        returncode = execute.execute(['cat'], stdout_cb, stderr_cb, stdin=stdin)
        self.assertEqual(0, returncode)
        self.assertEqual(expected, output)
        self.assertFalse(received_err)

    def test_execute_date(self):
        expected = datetime.datetime.now().strftime('%Y%m%d%H%M\n')
        output = ''
        received_err = False

        def stdout_cb(data):
            nonlocal output
            output += data

        def stderr_cb(data):
            nonlocal received_err
            received_err = True

        returncode = execute.execute(['date', '+%Y%m%d%H%M'], stdout_cb, stderr_cb)
        self.assertEqual(0, returncode)
        self.assertEqual(expected, output)
        self.assertFalse(received_err)

    def test_is_buffer_empty(self):
        stream = io.BytesIO()
        test_data = b'this is a test'
        output = None

        self.assertTrue(execute._is_buffer_empty(stream))

        stream.write(test_data)
        stream.seek(0)
        did_callback = execute.read_stream(stream, lambda x: None, stream.read())
        self.assertFalse(did_callback)
        self.assertFalse(execute._is_buffer_empty(stream))
        self.assertEqual(test_data, execute._buffers[stream])

        def set_output(data):
            nonlocal output
            output = data

        stream.write(b'\n')
        stream.seek(-1, os.SEEK_CUR)
        did_callback = execute.read_stream(stream, set_output, stream.read())
        self.assertTrue(did_callback)
        self.assertTrue(execute._is_buffer_empty(stream))
        self.assertEqual(test_data + b'\n', output.encode())

    def test_replace_all(self):
        check_pycolor_execute(self, ['free', '-h'], MOCKED_DATA, 'free_replace_all')

    def test_replace_fields_list(self):
        check_pycolor_execute(self, ['free', '-h'], MOCKED_DATA, 'free_replace_fields_list')

    @freeze_time('1997-01-31 12:34:56')
    def test_df_timestamp(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'df_timestamp')

    def test_df_table(self):
        check_pycolor_execute(self, ['df', '-h'], MOCKED_DATA, 'df_table')
