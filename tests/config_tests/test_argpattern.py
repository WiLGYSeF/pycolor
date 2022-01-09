import unittest

from src.pycolor.config.argpattern import ArgPattern

ARGLEN = 'arglen'
POSITION = 'position'
RANGE = 'range'

class GetArgPatternTest(unittest.TestCase):
    def test_get_arg_range(self):
        entries = [
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

        for entry in entries:
            arglen = entry[ARGLEN]
            position = entry[POSITION]
            with self.subTest(arglen=arglen, position=position):
                self.assertListEqual(
                    entry[RANGE],
                    list(ArgPattern({
                        'expression': '.*',
                        'position': position
                    }).get_arg_range(arglen))
                )

    def test_get_arg_range_fail(self):
        entries = [
            {
                ARGLEN: 4,
                POSITION: 'blah',
            },
        ]

        for entry in entries:
            arglen = entry[ARGLEN]
            position = entry[POSITION]
            with self.subTest(arglen=arglen, position=position):
                with self.assertRaises(Exception):
                    ArgPattern({
                        'expression': '.*',
                        'position': position
                    }).get_arg_range(arglen)
