import datetime
import io
import os
import unittest

import execute


class ExecuteTest(unittest.TestCase):
    def test_execute_date(self):
        def stdout_cb(data):
            self.assertEqual(
                data,
                datetime.datetime.now().strftime('%Y%m%d%H%M%S\n')
            )

        recv_stderr = False

        def stderr_cb(data):
            nonlocal recv_stderr
            recv_stderr = True

        returncode = execute.execute(['date', '+%Y%m%d%H%M%S'], stdout_cb, stderr_cb)
        self.assertEqual(returncode, 0)
        self.assertFalse(recv_stderr)

    def test_is_buffer_empty(self):
        stream = io.BytesIO()
        test_data = b'this is a test'
        output = None

        self.assertTrue(execute.is_buffer_empty(stream))

        stream.write(test_data)
        stream.seek(0)
        did_callback = execute.read_stream(stream, lambda x: None)
        self.assertFalse(did_callback)
        self.assertFalse(execute.is_buffer_empty(stream))
        self.assertEqual(execute.read_stream.buffers[stream], test_data)

        def set_output(data):
            nonlocal output
            output = data

        stream.write(b'\n')
        stream.seek(-1, os.SEEK_CUR)
        did_callback = execute.read_stream(stream, set_output)
        self.assertTrue(did_callback)
        self.assertTrue(execute.is_buffer_empty(stream))
        self.assertTrue(len(execute.read_stream.buffers[stream]) == 0)
        self.assertEqual(output.encode(), test_data + b'\n')
