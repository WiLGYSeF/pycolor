import unittest

from src.pycolor.search_replace import search_replace

class SearchReplaceTest(unittest.TestCase):
    def test_same_length_single(self):
        newstring, replace_ranges = search_replace(
            r'llo',
            'hello world',
            'wwo'
        )
        self.assertEqual('hewwo world', newstring)
        self.assertListEqual([
            (
                (2, 5),
                (2, 5)
            )
        ], replace_ranges)

    def test_same_length_two(self):
        newstring, replace_ranges = search_replace(
            r'[er]l',
            'hello world',
            '##'
        )
        self.assertEqual('h##lo wo##d', newstring)
        self.assertListEqual([
            (
                (1, 3),
                (1, 3)
            ),
            (
                (8, 10),
                (8, 10)
            )
        ], replace_ranges)

    def test_same_length_multi(self):
        newstring, replace_ranges = search_replace(
            r'l',
            'hello world',
            '##'
        )
        self.assertEqual('he####o wor##d', newstring)
        self.assertListEqual([
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
        ], replace_ranges)

    def test_shorter_single(self):
        newstring, replace_ranges = search_replace(
            r'e[a-z]{2}o',
            'hello world',
            '#'
        )
        self.assertEqual('h# world', newstring)
        self.assertListEqual([
            (
                (1, 5),
                (1, 2)
            )
        ], replace_ranges)

    def test_shorter_two(self):
        newstring, replace_ranges = search_replace(
            r'l+[a-z]',
            'hello world',
            '#'
        )
        self.assertEqual('he# wor#', newstring)
        self.assertListEqual([
            (
                (2, 5),
                (2, 3)
            ),
            (
                (9, 11),
                (7, 8)
            )
        ], replace_ranges)

    def test_longer_single(self):
        newstring, replace_ranges = search_replace(
            r'he',
            'hello world',
            '####'
        )
        self.assertEqual('####llo world', newstring)
        self.assertListEqual([
            (
                (0, 2),
                (0, 4)
            )
        ], replace_ranges)

    def test_longer_two(self):
        newstring, replace_ranges = search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234'
        )
        self.assertEqual('1234ello1234orld', newstring)
        self.assertListEqual([
            (
                (0, 1),
                (0, 4)
            ),
            (
                (5, 7),
                (8, 12)
            )
        ], replace_ranges)

    def test_two(self):
        newstring, replace_ranges = search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234'
        )
        self.assertEqual('1234ello1234orld', newstring)
        self.assertListEqual([
            (
                (0, 1),
                (0, 4)
            ),
            (
                (5, 7),
                (8, 12)
            )
        ], replace_ranges)

        newstring, replace_ranges = search_replace(
            r'l+[a-z]',
            newstring,
            '#'
        )
        self.assertEqual('1234e#1234or#', newstring)
        self.assertListEqual([
            (
                (5, 8),
                (5, 6)
            ),
            (
                (14, 16),
                (12, 13)
            )
        ], replace_ranges)

    def test_longer_two_ignore_first_between(self):
        newstring, replace_ranges = search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234',
            ignore_ranges=[
                (0, 2)
            ]
        )
        self.assertEqual('hello1234orld', newstring)
        self.assertListEqual([
            (
                (5, 7),
                (5, 9)
            )
        ], replace_ranges)

    def test_longer_two_ignore_second_between(self):
        newstring, replace_ranges = search_replace(
            r'^[a-z]|[^a-z][a-z]',
            'hello world',
            '1234',
            ignore_ranges=[
                (4, 6)
            ]
        )
        self.assertEqual('1234ello world', newstring)
        self.assertListEqual([
            (
                (0, 1),
                (0, 4)
            )
        ], replace_ranges)

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
        self.assertEqual('hello world', newstring)
        self.assertListEqual([], replace_ranges)

    def test_two_start_occurrence_two(self):
        newstring, replace_ranges = search_replace(
            r'o',
            'hello world',
            '#',
            start_occurrence=2
        )
        self.assertEqual('hello w#rld', newstring)
        self.assertListEqual([
            (
                (7, 8),
                (7, 8)
            )
        ], replace_ranges)

    def test_two_max_count_one(self):
        newstring, replace_ranges = search_replace(
            r'o',
            'hello world',
            '#',
            max_count=1
        )
        self.assertEqual('hell# world', newstring)
        self.assertListEqual([
            (
                (4, 5),
                (4, 5)
            )
        ], replace_ranges)

    def test_replace_all_ignore_between(self):
        newstring, replace_ranges = search_replace(
            r'^he(.*)ld',
            'hello world',
            'abc',
            ignore_ranges=[
                (3, 8)
            ]
        )
        self.assertEqual('hello world', newstring)
        self.assertListEqual([], replace_ranges)
