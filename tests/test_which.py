import unittest

from which import which


WHICH_PATH_SUCCESS = {
    'ls': [ '/bin/ls', '/usr/bin/ls' ],
    '/bin/ls': [ '/bin/ls', '/usr/bin/ls' ],
    'which': '/usr/bin/which',
    'useradd': '/usr/sbin/useradd'
}

WHICH_PATH_FAIL = [
    '0i1should2not3exist'
]


class WhichTest(unittest.TestCase):
    def test_which_success(self):
        for key, val in WHICH_PATH_SUCCESS.items():
            if isinstance(val, list):
                self.assertTrue(which(key) in val)
            else:
                self.assertEqual(which(key), val)

    def test_which_fail(self):
        for name in WHICH_PATH_FAIL:
            self.assertIsNone(which(name))
