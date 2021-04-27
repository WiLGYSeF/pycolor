import unittest

import arguments


ARGS = 'args'
SUBSET = 'subset'
RESULT = 'result'

CONSECUTIVE_END_ARGS = [
    {
        ARGS: [],
        SUBSET: [],
        RESULT: (True, 0)
    },
    {
        ARGS: ['--color', 'on', 'abc'],
        SUBSET: [],
        RESULT: (True, 3)
    },
    {
        ARGS: ['abc'],
        SUBSET: ['abc'],
        RESULT: (True, 0)
    },
    {
        ARGS: ['--color', 'on', 'abc'],
        SUBSET: ['abc'],
        RESULT: (True, 2)
    },
    {
        ARGS: ['--', 'asdf', '--color', 'on', 'abc'],
        SUBSET: ['asdf', '--color', 'on', 'abc'],
        RESULT: (True, 1)
    },
    {
        ARGS: ['asdf', '--color', 'on', 'abc'],
        SUBSET: ['asdf', 'abc'],
        RESULT: (False, 0)
    },
    {
        ARGS: ['asdf', 'abc', '--color', 'on'],
        SUBSET: ['asdf', 'abc'],
        RESULT: (False, 0)
    },
    {
        ARGS: ['asdf', 'abc', '--color', 'on'],
        SUBSET: ['nowhere'],
        RESULT: (False, 4)
    },
    {
        ARGS: ['asdf', 'abc', '--color', 'on'],
        SUBSET: ['abc'],
        RESULT: (False, 1)
    },
    {
        ARGS: ['ee', 'asdf', 'abc'],
        SUBSET: ['asdf', 'abc', '123', '4'],
        RESULT: (False, -1)
    },
]


class ArgumentsTest(unittest.TestCase):
    def test_consecutive_end_args(self):
        for entry in CONSECUTIVE_END_ARGS:
            self.assertTupleEqual(
                arguments.consecutive_end_args(entry[ARGS], entry[SUBSET]),
                entry[RESULT]
            )
