import unittest

from src.pycolor import arguments

ARGS = 'args'
ACTIONS = 'actions'
RESULT = 'result'

class MockAction:
    def __init__(self, option_strings, nargs):
        self.option_strings = option_strings
        self.nargs = nargs

class ArgumentsTest(unittest.TestCase):
    def test_split_args_normal(self):
        entries = [
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

        for entry in entries:
            args = entry[ARGS]
            actions = entry[ACTIONS]
            with self.subTest(args=args, actions=actions):
                self.assertTupleEqual(
                    entry[RESULT],
                    arguments.split_args(args, actions)
                )

    def test_split_args_nargs_int(self):
        entries = [
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

        for entry in entries:
            args = entry[ARGS]
            actions = entry[ACTIONS]
            with self.subTest(args=args, actions=actions):
                self.assertTupleEqual(
                    entry[RESULT],
                    arguments.split_args(args, actions)
                )

    def test_split_args_nargs_question(self):
        entries = [
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

        for entry in entries:
            args = entry[ARGS]
            actions = entry[ACTIONS]
            with self.subTest(args=args, actions=actions):
                self.assertTupleEqual(
                    entry[RESULT],
                    arguments.split_args(args, actions)
                )

    def test_split_args_nargs_star(self):
        entries = [
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

        for entry in entries:
            args = entry[ARGS]
            actions = entry[ACTIONS]
            with self.subTest(args=args, actions=actions):
                self.assertTupleEqual(
                    entry[RESULT],
                    arguments.split_args(args, actions)
                )

    def test_split_args_nargs_plus(self):
        entries = [
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

        for entry in entries:
            args = entry[ARGS]
            actions = entry[ACTIONS]
            with self.subTest(args=args, actions=actions):
                self.assertTupleEqual(
                    entry[RESULT],
                    arguments.split_args(args, actions)
                )

    def test_split_args_nargs_none(self):
        entries = [
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

        for entry in entries:
            args = entry[ARGS]
            actions = entry[ACTIONS]
            with self.subTest(args=args, actions=actions):
                self.assertTupleEqual(
                    entry[RESULT],
                    arguments.split_args(args, actions)
                )

    def test_split_args_nargs_dashdash(self):
        entries = [
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

        for entry in entries:
            args = entry[ARGS]
            actions = entry[ACTIONS]
            with self.subTest(args=args, actions=actions):
                self.assertTupleEqual(
                    entry[RESULT],
                    arguments.split_args(args, actions)
                )
