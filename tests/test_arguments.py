import unittest

from src.pycolor import arguments


ARGS = 'args'
ACTIONS = 'actions'
RESULT = 'result'

class MockAction:
    def __init__(self, option_strings, nargs):
        self.option_strings = option_strings
        self.nargs = nargs

SPLIT_ARGS_NORMAL = [
    {
        ARGS: [],
        ACTIONS: [],
        RESULT: (
            [],
            []
        )
    },
    {
        ARGS: ['abc', '-a', '-b'],
        ACTIONS: [
            MockAction(['-a'], 0),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            [],
            ['abc', '-a', '-b']
        )
    },
    {
        ARGS: ['-a', '-b'],
        ACTIONS: [
            MockAction(['-a'], 0),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', '-b'],
            []
        )
    },
    {
        ARGS: ['-a', 'abc', '-b'],
        ACTIONS: [
            MockAction(['-a'], 0),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a'],
            ['abc', '-b']
        )
    },
]

SPLIT_ARGS_NARGS_INT = [
    {
        ARGS: ['-a', 'abc', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], 1),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc', '-b'],
            ['zzz']
        )
    },
    {
        ARGS: ['-a', 'abc', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], 2),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc'],
            ['-b', 'zzz']
        )
    },
    {
        ARGS: ['-a', 'abc', 'def', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], 2),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc', 'def', '-b'],
            ['zzz']
        )
    },
]

SPLIT_ARGS_NARGS_QUESTION = [
    {
        ARGS: ['-a', 'abc', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], '?'),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc', '-b'],
            ['zzz']
        )
    },
    {
        ARGS: ['-a', 'abc', 'def', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], '?'),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc'],
            ['def', '-b', 'zzz']
        )
    },
    {
        ARGS: ['-a', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], '?'),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', '-b'],
            ['zzz']
        )
    },
]

SPLIT_ARGS_NARGS_STAR = [
    {
        ARGS: ['-a', 'abc', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], '*'),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc', '-b'],
            ['zzz']
        )
    },
    {
        ARGS: ['-a', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], '*'),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', '-b'],
            ['zzz']
        )
    },
    {
        ARGS: ['-a', 'abc', 'def', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], '*'),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc', 'def', '-b'],
            ['zzz']
        )
    },
]

SPLIT_ARGS_NARGS_PLUS = [
    {
        ARGS: ['-a', 'abc', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], '+'),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc', '-b'],
            ['zzz']
        )
    },
    {
        ARGS: ['-a', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], '+'),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', '-b'],
            ['zzz']
        )
    },
    {
        ARGS: ['-a', 'abc', 'def', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], '+'),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc', 'def', '-b'],
            ['zzz']
        )
    },
]

SPLIT_ARGS_NARGS_NONE = [
    {
        ARGS: ['-a', 'abc', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], None),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc', '-b'],
            ['zzz']
        )
    },
    {
        ARGS: ['-a', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], None),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', '-b'],
            ['zzz']
        )
    },
    {
        ARGS: ['-a', 'abc', 'def', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], None),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc'],
            ['def', '-b', 'zzz']
        )
    },
]

SPLIT_ARGS_NARGS_DASHDASH = [
    {
        ARGS: ['-a', '--', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], 0),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a'],
            ['-b', 'zzz']
        )
    },
    {
        ARGS: ['-a', 'abc', '--', 'def', '-b', 'zzz'],
        ACTIONS: [
            MockAction(['-a'], '+'),
            MockAction(['-b'], 0),
        ],
        RESULT: (
            ['-a', 'abc'],
            ['def', '-b', 'zzz']
        )
    },
]


class ArgumentsTest(unittest.TestCase):
    def test_split_args_normal(self):
        for entry in SPLIT_ARGS_NORMAL:
            self.assertTupleEqual(
                arguments.split_args(entry[ARGS], entry[ACTIONS]),
                entry[RESULT]
            )

    def test_split_args_nargs_int(self):
        for entry in SPLIT_ARGS_NARGS_INT:
            self.assertTupleEqual(
                arguments.split_args(entry[ARGS], entry[ACTIONS]),
                entry[RESULT]
            )

    def test_split_args_nargs_question(self):
        for entry in SPLIT_ARGS_NARGS_QUESTION:
            self.assertTupleEqual(
                arguments.split_args(entry[ARGS], entry[ACTIONS]),
                entry[RESULT]
            )

    def test_split_args_nargs_star(self):
        for entry in SPLIT_ARGS_NARGS_STAR:
            self.assertTupleEqual(
                arguments.split_args(entry[ARGS], entry[ACTIONS]),
                entry[RESULT]
            )

    def test_split_args_nargs_plus(self):
        for entry in SPLIT_ARGS_NARGS_PLUS:
            self.assertTupleEqual(
                arguments.split_args(entry[ARGS], entry[ACTIONS]),
                entry[RESULT]
            )

    def test_split_args_nargs_none(self):
        for entry in SPLIT_ARGS_NARGS_NONE:
            self.assertTupleEqual(
                arguments.split_args(entry[ARGS], entry[ACTIONS]),
                entry[RESULT]
            )

    def test_split_args_nargs_dashdash(self):
        for entry in SPLIT_ARGS_NARGS_DASHDASH:
            self.assertTupleEqual(
                arguments.split_args(entry[ARGS], entry[ACTIONS]),
                entry[RESULT]
            )
