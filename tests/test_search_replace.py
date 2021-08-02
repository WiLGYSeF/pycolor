import unittest

from src.pycolor.search_replace import search_replace


# TODO: more test cases
class SearchReplaceTest(unittest.TestCase):
    def test_same_length_single(self):
        newstring, replace_ranges = search_replace(
            r'llo',
            'hello world',
            'wwo'
        )
        self.assertEqual(newstring, 'hewwo world')
        self.assertListEqual(replace_ranges, [
            (
                (2, 5),
                (2, 5)
            )
        ])

    def test_same_length_two(self):
        newstring, replace_ranges = search_replace(
            r'[er]l',
            'hello world',
            '##'
        )
        self.assertEqual(newstring, 'h##lo wo##d')
        self.assertListEqual(replace_ranges, [
            (
                (1, 3),
                (1, 3)
            ),
            (
                (8, 10),
                (8, 10)
            )
        ])

    def test_same_length_multi(self):
        newstring, replace_ranges = search_replace(
            r'l',
            'hello world',
            '##'
        )
        self.assertEqual(newstring, 'he####o wor##d')
        self.assertListEqual(replace_ranges, [
            (
                (2, 3),
                (2, 4)
            ),
            (
                (3, 4),
                (4, 6)
            ),
            (
                (9, 10),
                (11, 13)
            )
        ])

    def test_shorter_single(self):
        newstring, replace_ranges = search_replace(
            r'e[a-z]{2}o',
            'hello world',
            '#'
        )
        self.assertEqual(newstring, 'h# world')
        self.assertListEqual(replace_ranges, [
            (
                (1, 5),
                (1, 2)
            )
        ])

    def test_shorter_two(self):
        newstring, replace_ranges = search_replace(
            r'l+[a-z]',
            'hello world',
            '#'
        )
        self.assertEqual(newstring, 'he# wor#')
        self.assertListEqual(replace_ranges, [
            (
                (2, 5),
                (2, 3)
            ),
            (
                (9, 11),
                (7, 8)
            )
        ])

    def test_longer_single(self):
        newstring, replace_ranges = search_replace(
            r'he',
            'hello world',
            '####'
        )
        self.assertEqual(newstring, '####llo world')
        self.assertListEqual(replace_ranges, [
            (
                (0, 2),
                (0, 4)
            )
        ])

    def test_longer_two(self):
        newstring, replace_ranges = search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234'
        )
        self.assertEqual(newstring, '1234ello1234orld')
        self.assertListEqual(replace_ranges, [
            (
                (0, 1),
                (0, 4)
            ),
            (
                (5, 7),
                (8, 12)
            )
        ])

    def test_two(self):
        newstring, replace_ranges = search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234'
        )
        self.assertEqual(newstring, '1234ello1234orld')
        self.assertListEqual(replace_ranges, [
            (
                (0, 1),
                (0, 4)
            ),
            (
                (5, 7),
                (8, 12)
            )
        ])

        newstring, replace_ranges = search_replace(
            r'l+[a-z]',
            newstring,
            '#'
        )
        self.assertEqual(newstring, '1234e#1234or#')
        self.assertListEqual(replace_ranges, [
            (
                (5, 8),
                (5, 6)
            ),
            (
                (14, 16),
                (12, 13)
            )
        ])

    def test_longer_two_ignore_first_between(self):
        newstring, replace_ranges = search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234',
            ignore_ranges=[
                (0, 2)
            ]
        )
        self.assertEqual(newstring, 'hello1234orld')
        self.assertListEqual(replace_ranges, [
            (
                (5, 7),
                (5, 9)
            )
        ])

    def test_longer_two_ignore_second_between(self):
        newstring, replace_ranges = search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234',
            ignore_ranges=[
                (4, 6)
            ]
        )
        self.assertEqual(newstring, '1234ello world')
        self.assertListEqual(replace_ranges, [
            (
                (0, 1),
                (0, 4)
            )
        ])

    def test_longer_two_ignore_all_between(self):
        newstring, replace_ranges = search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234',
            ignore_ranges=[
                (0, 2),
                (4, 6)
            ]
        )
        self.assertEqual(newstring, 'hello world')
        self.assertListEqual(replace_ranges, [])

    def test_two_start_occurrence_two(self):
        newstring, replace_ranges = search_replace(
            r'o',
            'hello world',
            '#',
            start_occurrence=2
        )
        self.assertEqual(newstring, 'hello w#rld')
        self.assertListEqual(replace_ranges, [
            (
                (7, 8),
                (7, 8)
            )
        ])

    def test_two_max_count_one(self):
        newstring, replace_ranges = search_replace(
            r'o',
            'hello world',
            '#',
            max_count=1
        )
        self.assertEqual(newstring, 'hell# world')
        self.assertListEqual(replace_ranges, [
            (
                (4, 5),
                (4, 5)
            )
        ])

    def test_replace_all_ignore_between(self):
        newstring, replace_ranges = search_replace(
            r'^he(.*)ld',
            'hello world',
            'abc',
            ignore_ranges=[
                (3, 8)
            ]
        )
        self.assertEqual(newstring, 'hello world')
        self.assertListEqual(replace_ranges, [])
