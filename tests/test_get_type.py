import unittest

from get_type import get_type


VALUE = 'value'
VALUE_TYPE = 'value_type'
RESULT = 'result'

GET_TYPE = [
    {
        VALUE: 'abc',
        VALUE_TYPE: str,
        RESULT: 'abc'
    },
    {
        VALUE: 'abc',
        VALUE_TYPE: int,
        RESULT: None
    },
    {
        VALUE: 4,
        VALUE_TYPE: int,
        RESULT: 4
    },
    {
        VALUE: '4',
        VALUE_TYPE: int,
        RESULT: None
    },
    {
        VALUE: [1, 2, 3],
        VALUE_TYPE: list,
        RESULT: [1, 2, 3]
    },
    {
        VALUE: 'abc',
        VALUE_TYPE: list,
        RESULT: None
    },
    {
        VALUE: 4,
        VALUE_TYPE: (str, int),
        RESULT: 4
    },
]


class GetTypeTest(unittest.TestCase):
    def test_get_type(self):
        for entry in GET_TYPE:
            self.assertEqual(get_type(
                {
                    'test': entry[VALUE]
                },
                'test',
                entry[VALUE_TYPE],
                default=None
            ), entry[RESULT])
