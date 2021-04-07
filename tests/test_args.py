import unittest

import args


ARGV = 'argv'
MY_ARGS = 'my_args'
CMD_ARGS = 'cmd_args'
START_IDX = 'start_idx'

GET_MY_ARGS = [
    {
        ARGV: [],
        MY_ARGS: [],
        CMD_ARGS: [],
        START_IDX: 0
    },
    {
        ARGV: ['ls'],
        MY_ARGS: [],
        CMD_ARGS: ['ls'],
        START_IDX: 0
    },
    {
        ARGV: ['pycolor'],
        MY_ARGS: [],
        CMD_ARGS: [],
        START_IDX: 1
    },
    {
        ARGV: ['ls', '-l'],
        MY_ARGS: [],
        CMD_ARGS: ['ls', '-l'],
        START_IDX: 0
    },
    {
        ARGV: ['pycolor', 'ls', '-l'],
        MY_ARGS: [],
        CMD_ARGS: ['ls', '-l'],
        START_IDX: 1
    },
    {
        ARGV: ['pycolor', '--color', 'ls', '-l'],
        MY_ARGS: ['--color'],
        CMD_ARGS: ['ls', '-l'],
        START_IDX: 1
    },
    {
        ARGV: ['pycolor', '--test', '--color', 'ls', '-l'],
        MY_ARGS: ['--test', '--color'],
        CMD_ARGS: ['ls', '-l'],
        START_IDX: 1
    },
    {
        ARGV: ['pycolor', '--test', 'abc', '--color', 'ls', '-l'],
        MY_ARGS: ['--test'],
        CMD_ARGS: ['abc', '--color', 'ls', '-l'],
        START_IDX: 1
    },
    {
        ARGV: ['pycolor', '--color', '--', 'ls', '-l'],
        MY_ARGS: ['--color'],
        CMD_ARGS: ['ls', '-l'],
        START_IDX: 1
    },
    {
        ARGV: ['pycolor', '--', '--weirdname'],
        MY_ARGS: [],
        CMD_ARGS: ['--weirdname'],
        START_IDX: 1
    },
]

GET_ARGS = {
    'invalid': ValueError(),
    '--asdf': ('asdf', None),
    '--asdf=': ('asdf', ''),
    '--asdf=test': ('asdf', 'test')
}


class ArgsTest(unittest.TestCase):
    def test_get_my_args(self):
        for entry in GET_MY_ARGS:
            my_args, cmd_args = args.get_my_args(entry[ARGV], start_idx=entry[START_IDX])
            self.assertListEqual(my_args, entry[MY_ARGS])
            self.assertListEqual(cmd_args, entry[CMD_ARGS])

    def test_get_arg(self):
        for string, val in GET_ARGS.items():
            if isinstance(val, Exception):
                self.assertRaises(Exception, args.get_arg, string)
            else:
                self.assertTupleEqual(args.get_arg(string), val)
