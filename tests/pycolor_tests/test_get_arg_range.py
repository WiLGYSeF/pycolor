import unittest

from pycolor_class import Pycolor


ARGLEN = 'arglen'
POSITION = 'position'
RANGE = 'range'

GET_ARG_RANGES = [
    {
        ARGLEN: 4,
        POSITION: None,
        RANGE: [0, 1, 2, 3],
    },
    {
        ARGLEN: 4,
        POSITION: '*',
        RANGE: [0, 1, 2, 3],
    },
    {
        ARGLEN: 4,
        POSITION: 'blah',
        RANGE: [0, 1, 2, 3],
    },
    {
        ARGLEN: 4,
        POSITION: '1',
        RANGE: [0],
    },
    {
        ARGLEN: 4,
        POSITION: '2',
        RANGE: [1],
    },
    {
        ARGLEN: 4,
        POSITION: '3',
        RANGE: [2],
    },
    {
        ARGLEN: 4,
        POSITION: '4',
        RANGE: [3],
    },
    {
        ARGLEN: 4,
        POSITION: '5',
        RANGE: [],
    },
    {
        ARGLEN: 4,
        POSITION: '+2',
        RANGE: [1, 2, 3],
    },
    {
        ARGLEN: 4,
        POSITION: '-3',
        RANGE: [0, 1, 2],
    },
    {
        ARGLEN: 4,
        POSITION: '>8',
        RANGE: [],
    },
    {
        ARGLEN: 4,
        POSITION: '<8',
        RANGE: [0, 1, 2, 3],
    },
    {
        ARGLEN: 4,
        POSITION: 8,
        RANGE: [],
    },
    {
        ARGLEN: 4,
        POSITION: 3,
        RANGE: [2],
    },
]


class GetArgRangeTest(unittest.TestCase):
    def test_get_arg_range(self):
        for entry in GET_ARG_RANGES:
            self.assertListEqual(
                list(Pycolor.get_arg_range(entry[ARGLEN], entry[POSITION])),
                entry[RANGE]
            )
