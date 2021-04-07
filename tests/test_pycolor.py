import unittest

import pycolor


ARGS = 'args'
SUBSET = 'subset'
RESULT = 'result'

CONSECUTIVE_END_ARGS = [
    {
        ARGS: [],
        SUBSET: [],
        RESULT: True
    },
    {
        ARGS: ['--color', 'on', 'abc'],
        SUBSET: [],
        RESULT: True
    },
    {
        ARGS: ['abc'],
        SUBSET: ['abc'],
        RESULT: True
    },
    {
        ARGS: ['--color', 'on', 'abc'],
        SUBSET: ['abc'],
        RESULT: True
    },
    {
        ARGS: ['--', 'asdf', '--color', 'on', 'abc'],
        SUBSET: ['asdf', '--color', 'on', 'abc'],
        RESULT: True
    },
    {
        ARGS: ['asdf', '--color', 'on', 'abc'],
        SUBSET: ['asdf', 'abc'],
        RESULT: False
    },
    {
        ARGS: ['asdf', 'abc', '--color', 'on'],
        SUBSET: ['asdf', 'abc'],
        RESULT: False
    },
    {
        ARGS: ['asdf', 'abc', '--color', 'on'],
        SUBSET: ['nowhere'],
        RESULT: False
    },
    {
        ARGS: ['asdf', 'abc', '--color', 'on'],
        SUBSET: ['abc'],
        RESULT: False
    },
    {
        ARGS: ['ee', 'asdf', 'abc'],
        SUBSET: ['asdf', 'abc', '123', '4'],
        RESULT: False
    },
]


class ArgsTest(unittest.TestCase):
    def test_consecutive_end_args(self):
        for entry in CONSECUTIVE_END_ARGS:
            self.assertEqual(
                pycolor.consecutive_end_args(entry[ARGS], entry[SUBSET]),
                entry[RESULT]
            )
