import unittest

from argpattern import ArgPattern
from pycolor_class import Pycolor


ARGS = 'args'
ARGPATTERNS = 'argpatterns'
RESULT = 'result'

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


class CheckArgPatternsTest(unittest.TestCase):
    def test_check_arg_patterns(self):
        for entry in CHECK_ARG_PATTERNS:
            argpats = map(lambda x: ArgPattern(x), entry[ARGPATTERNS])
            self.assertEqual(
                Pycolor.check_arg_patterns(entry[ARGS], argpats),
                entry[RESULT]
            )
