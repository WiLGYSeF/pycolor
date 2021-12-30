import unittest

from src.pycolor.config import ConfigPropertyError
from src.pycolor.config.pattern import Pattern, bsearch_closest

ACTIVATIONS = 'activations'
DEACTIVATIONS = 'deactivations'
RESULT = 'result'
ARRAY = 'array'
VALUE = 'value'

class PatternTest(unittest.TestCase):
    def test_min_max_fields_fail(self):
        with self.assertRaises(ConfigPropertyError):
            Pattern({
                'separator': ' +',
                'min_fields': 5,
                'max_fields': 4,
            })

    def test_get_activation_ranges(self):
        entries = [
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

        for entry in entries:
            activations = entry[ACTIVATIONS]
            deactivations = entry[DEACTIVATIONS]
            with self.subTest(activations=activations, deactivations=deactivations):
                self.assertListEqual(
                    entry[RESULT],
                    Pattern.get_activation_ranges(activations, deactivations),
                )

    def test_bsearch_closest(self):
        entries = [
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

        for entry in entries:
            array = entry[ARRAY]
            value = entry[VALUE]
            with self.subTest(array=array, value=value):
                self.assertEqual(entry[RESULT], bsearch_closest(array, value))
