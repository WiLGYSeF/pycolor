import unittest

from src.pycolor.config import ConfigPropertyError
from src.pycolor.config.pattern import Pattern, bsearch_closest


ACTIVATIONS = 'activations'
DEACTIVATIONS = 'deactivations'
RESULT = 'result'

GET_ACTIVATION_RANGES = [
    {
        ACTIVATIONS: [],
        DEACTIVATIONS: [],
        RESULT: []
    },
    {
        ACTIVATIONS: [1, 5, 12],
        DEACTIVATIONS: [3, 11],
        RESULT: [(1, True), (3, False), (5, True), (11, False), (12, True)]
    },
    {
        ACTIVATIONS: [1, 5, 9, 12],
        DEACTIVATIONS: [3, 4, 11],
        RESULT: [(1, True), (3, False), (5, True), (11, False), (12, True)]
    },
    {
        ACTIVATIONS: [1, 5, 12],
        DEACTIVATIONS: [],
        RESULT: [(1, True)]
    },
    {
        ACTIVATIONS: [],
        DEACTIVATIONS: [3, 11],
        RESULT: [(3, False)]
    },
    {
        ACTIVATIONS: [1],
        DEACTIVATIONS: [-1],
        RESULT: [(1, True)]
    },
]

ARRAY = 'array'
VALUE = 'value'
RESULT = 'result'

BSEARCH_CLOSEST = [
    {
        ARRAY: [],
        VALUE: 4,
        RESULT: (0, False)
    },
    {
        ARRAY: [1],
        VALUE: 4,
        RESULT: (1, False)
    },
    {
        ARRAY: [7],
        VALUE: 4,
        RESULT: (0, False)
    },
    {
        ARRAY: [4],
        VALUE: 4,
        RESULT: (0, True)
    },
    {
        ARRAY: [1, 3, 7, 12, 15],
        VALUE: 3,
        RESULT: (1, True)
    },
    {
        ARRAY: [1, 3, 7, 12, 15],
        VALUE: 1,
        RESULT: (0, True)
    },
    {
        ARRAY: [1, 3, 7, 9, 12, 15],
        VALUE: 15,
        RESULT: (5, True)
    },
    {
        ARRAY: [1, 3, 7, 9, 12, 15],
        VALUE: 6,
        RESULT: (2, False)
    },
    {
        ARRAY: [1, 3, 7, 9, 12, 15],
        VALUE: 4,
        RESULT: (2, False)
    },
    {
        ARRAY: [1, 3, 7, 12, 15],
        VALUE: 0,
        RESULT: (0, False)
    },
    {
        ARRAY: [1, 3, 7, 12, 15],
        VALUE: 16,
        RESULT: (5, False)
    },
    {
        ARRAY: [1, 3, 7, 12, 15],
        VALUE: 11,
        RESULT: (3, False)
    },
]


class PatternTest(unittest.TestCase):
    def test_min_max_fields_fail(self):
        with self.assertRaises(ConfigPropertyError):
            Pattern({
                'separator': ' +',
                'min_fields': 5,
                'max_fields': 4,
            })

    def test_get_activation_ranges(self):
        for entry in GET_ACTIVATION_RANGES:
            self.assertListEqual(
                Pattern.get_activation_ranges(
                    entry[ACTIVATIONS],
                    entry[DEACTIVATIONS]
                ),
                entry[RESULT]
            )

    def test_bsearch_closest(self):
        for entry in BSEARCH_CLOSEST:
            self.assertEqual(
                bsearch_closest(entry[ARRAY], entry[VALUE]),
                entry[RESULT]
            )
