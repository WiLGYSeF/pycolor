import unittest

from pycolor_class import Pycolor

ARGS = 'args'
ARGPATTERNS = 'argpatterns'
RESULT = 'result'

ARGLEN = 'arglen'
POSITION = 'position'
RANGE = 'range'

CHECK_ARG_PATTERNS = [
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-l',
                'position': '*',
                'match_not': False,
                'optional': False
            }
        ],
        RESULT: True
    },
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-a',
                'position': '*',
                'match_not': False,
                'optional': False
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['-lA'],
        ARGPATTERNS: [
            {
                'expression': '-[A-Za-z]*l[A-Za-z]*',
                'position': '*',
                'match_not': False,
                'optional': False
            }
        ],
        RESULT: True
    },
    {
        ARGS: ['-l', '-a'],
        ARGPATTERNS: [
            {
                'expression': '-l',
                'position': 1,
                'match_not': False,
                'optional': False
            }
        ],
        RESULT: True
    },
    {
        ARGS: ['-l', '-a'],
        ARGPATTERNS: [
            {
                'expression': '-l',
                'position': 2,
                'match_not': False,
                'optional': False
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-l',
                'position': '*',
                'match_not': True,
                'optional': False
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-l',
                'position': '*',
                'match_not': False,
                'optional': False
            },
            {
                'expression': '-a',
                'position': '*',
                'match_not': False,
                'optional': False
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-l',
                'position': '*',
                'match_not': False,
                'optional': False
            },
            {
                'expression': '-a',
                'position': '*',
                'match_not': False,
                'optional': True
            }
        ],
        RESULT: True
    },
]

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


class PycolorClassTest(unittest.TestCase):
    def test_check_arg_patterns(self):
        for entry in CHECK_ARG_PATTERNS:
            self.assertEqual(
                Pycolor.check_arg_patterns(entry[ARGS], entry[ARGPATTERNS]),
                entry[RESULT]
            )

    def test_get_arg_range(self):
        for entry in GET_ARG_RANGES:
            self.assertListEqual(
                list(Pycolor.get_arg_range(entry[ARGLEN], entry[POSITION])),
                entry[RANGE]
            )
