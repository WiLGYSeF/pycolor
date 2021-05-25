import datetime
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
