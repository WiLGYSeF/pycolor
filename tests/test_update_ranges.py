import unittest

import pycolor


# TODO: more test cases
class UpdateRangesTest(unittest.TestCase):
    def test_abc(self):
        ranges = []
        newstring, replace_ranges = pycolor.search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234'
        )
        self.assertEqual(newstring, '1234ello1234orld')

        pycolor.update_ranges(ranges, replace_ranges)
        self.assertListEqual(ranges, [
            (0, 4),
            (8, 12)
        ])

        newstring, replace_ranges = pycolor.search_replace(
            r'l+[a-z]',
            newstring,
            '#'
        )
        self.assertEqual(newstring, '1234e#1234or#')

        pycolor.update_ranges(ranges, replace_ranges)
        self.assertListEqual(ranges, [
            (0, 4),
            (5, 6),
            (6, 10),
            (12, 13)
        ])
