import datetime
import io
import os
import unittest

from src.pycolor.execute import execute

class ExecuteTest(unittest.TestCase):
    def test_execute_date(self):
        def stdout_cb(data):
            self.assertEqual(
                datetime.datetime.now().strftime('%Y%m%d%H%M%S\n'),
                data
            )

        def stderr_cb(data):
            self.assertFalse(True)

        returncode = execute.execute(['date', '+%Y%m%d%H%M%S'], stdout_cb, stderr_cb)
        self.assertEqual(0, returncode)

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
