import unittest

from search_replace import search_replace, update_ranges


# TODO: more test cases
class UpdateRangesTest(unittest.TestCase):
    def test_abc(self):
        ranges = []
        newstring, replace_ranges = search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234'
        )
        self.assertEqual(newstring, '1234ello1234orld')

        update_ranges(ranges, replace_ranges)
        self.assertListEqual(ranges, [
            (0, 4),
            (8, 12)
        ])

        newstring, replace_ranges = search_replace(
            r'l+[a-z]',
            newstring,
            '#'
        )
        self.assertEqual(newstring, '1234e#1234or#')

        update_ranges(ranges, replace_ranges)
        self.assertListEqual(ranges, [
            (0, 4),
            (5, 6),
            (6, 10),
            (12, 13)
        ])
