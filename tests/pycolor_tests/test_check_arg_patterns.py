import re
import unittest

from pycolor_class import Pycolor


ARGS = 'args'
ARGPATTERNS = 'argpatterns'
RESULT = 'result'

CHECK_ARG_PATTERNS = [
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'regex': re.compile('-l'),
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
                'regex': re.compile('-a'),
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
                'regex': re.compile('-[A-Za-z]*l[A-Za-z]*'),
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
                'regex': re.compile('-l'),
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
                'regex': re.compile('-l'),
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
                'regex': re.compile('-l'),
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
                'regex': re.compile('-l'),
                'position': '*',
                'match_not': False,
                'optional': False
            },
            {
                'regex': re.compile('-a'),
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
                'regex': re.compile('-l'),
                'position': '*',
                'match_not': False,
                'optional': False
            },
            {
                'regex': re.compile('-a'),
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
            self.assertEqual(
                Pycolor.check_arg_patterns(entry[ARGS], entry[ARGPATTERNS]),
                entry[RESULT]
            )
