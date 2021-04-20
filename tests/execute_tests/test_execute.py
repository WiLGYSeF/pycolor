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

        def stderr_cb(data):
            self.assertTrue(False)

        returncode = execute.execute(['date', '+%Y%m%d%H%M%S'], stdout_cb, stderr_cb)
        self.assertEqual(returncode, 0)
