import os
import sys
import unittest

from config import ConfigPropertyError
from config.argpattern import ArgPattern
import printmsg
from profileloader import ProfileLoader
from tests.execute_tests.helpers import textstream
from tests.testutils import patch

ARGS = 'args'
ARGPATTERNS = 'argpatterns'
RESULT = 'result'

CHECK_ARG_PATTERNS = [
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-l',
            }
        ],
        RESULT: True
    },
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-a',
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['-lA'],
        ARGPATTERNS: [
            {
                'expression': '-[A-Za-z]*l[A-Za-z]*',
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
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-l',
            },
            {
                'expression': '-a',
            }
        ],
        RESULT: False
    },
]

CHECK_ARG_PATTERNS_MATCH_NOT = [
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-l',
                'match_not': True,
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-a',
                'match_not': True,
            }
        ],
        RESULT: True
    },
]

CHECK_ARG_PATTERNS_OPTIONAL = [
    {
        ARGS: ['-l'],
        ARGPATTERNS: [
            {
                'expression': '-l',
            },
            {
                'expression': '-a',
                'position': '*',
                'optional': True
            }
        ],
        RESULT: True
    },
    {
        ARGS: [],
        ARGPATTERNS: [
            {
                'expression': '-l',
                'optional': True
            },
            {
                'expression': '-a',
                'optional': True
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['-a'],
        ARGPATTERNS: [
            {
                'expression': '-l',
                'optional': True
            },
            {
                'expression': '-a',
                'optional': True
            }
        ],
        RESULT: True
    },
]

CHECK_ARG_PATTERNS_SUBCOMMAND = [
    {
        ARGS: ['add', 'entry', '-v'],
        ARGPATTERNS: [
            {
                'subcommand': ['add'],
            }
        ],
        RESULT: True
    },
    {
        ARGS: ['add', 'entry', '-v', 'last'],
        ARGPATTERNS: [
            {
                'subcommand': ['add', 'entry', 'last'],
            }
        ],
        RESULT: True
    },
    {
        ARGS: ['add', 'entry', '-v'],
        ARGPATTERNS: [
            {
                'subcommand': ['add', 'entry', 'last'],
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['add', 'entry', '-v', 'last'],
        ARGPATTERNS: [
            {
                'subcommand': ['add', 'entry', 'first'],
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['add', 'entry', '-v', '--', 'last'],
        ARGPATTERNS: [
            {
                'subcommand': ['add', 'entry', 'last'],
            }
        ],
        RESULT: False
    },
    {
        ARGS: ['remove', 'entry', '-v'],
        ARGPATTERNS: [
            {
                'subcommand': [None, 'entry'],
            }
        ],
        RESULT: True
    },
    {
        ARGS: ['-v', 'add', 'entry'],
        ARGPATTERNS: [
            {
                'subcommand': ['add', 'entry'],
            }
        ],
        RESULT: True
    },
    {
        ARGS: ['-v', 'add', 'entry'],
        ARGPATTERNS: [
            {
                'subcommand': 'add',
            }
        ],
        RESULT: True
    },
]

MOCKED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocked_data')


class ProfileLoaderTest(unittest.TestCase):
    def test_load_file_same_profile_name(self):
        loader = ProfileLoader()
        stderr = textstream()

        with patch(sys, 'stderr', stderr), patch(printmsg, 'is_color_enabled', lambda x: True):
            loader.load_file(os.path.join(MOCKED_DATA, 'load-file-same-profile-name.json'))
        stderr.seek(0)
        self.assertEqual(
            stderr.read(),
            '\x1b[93mwarn\x1b[0m: conflicting profiles with the name "test"\n'
        )

    def test_from_profile_separate_file(self):
        loader = ProfileLoader()
        loader.load_file(os.path.join(MOCKED_DATA, 'from-profile-separate-file1.json'))
        loader.load_file(os.path.join(MOCKED_DATA, 'from-profile-separate-file2.json'))

        prof = loader.get_profile_by_name('test')
        numbers = loader.get_profile_by_name('numbers')
        self.assertEqual(prof.loaded_patterns[0].expression, numbers.patterns[0]['expression'])

    def test_include_from_profile_fail(self):
        loader = ProfileLoader()
        with self.assertRaises(ConfigPropertyError):
            loader.load_file(os.path.join(MOCKED_DATA, 'include-from-profile-fail.json'))
            loader.get_profile_by_name('asdf').loaded_patterns

    def test_get_profile_by_command_which(self):
        loader = ProfileLoader()
        loader.load_file(os.path.join(MOCKED_DATA, 'get-profile-by-command-which.json'))

        self.assertEqual(
            loader.get_profile_by_command('date', []),
            loader.get_profile_by_name('which')
        )
        self.assertIsNone(loader.get_profile_by_command('noexist', []))

    def test_get_profile_by_command_which_ignore_case(self):
        loader = ProfileLoader()
        loader.load_file(os.path.join(MOCKED_DATA, 'get-profile-by-command-which-ignore-case.json'))

        self.assertEqual(
            loader.get_profile_by_command('date', []),
            loader.get_profile_by_name('which-ignore-case')
        )
        self.assertIsNone(loader.get_profile_by_command('noexist', []))

    def test_check_arg_patterns(self):
        for entry in CHECK_ARG_PATTERNS:
            argpats = list(map(lambda x: ArgPattern(x), entry[ARGPATTERNS]))
            self.assertEqual(
                ProfileLoader.check_arg_patterns(entry[ARGS], argpats),
                entry[RESULT]
            )

    def test_check_arg_patterns_match_not(self):
        for entry in CHECK_ARG_PATTERNS_MATCH_NOT:
            argpats = list(map(lambda x: ArgPattern(x), entry[ARGPATTERNS]))
            self.assertEqual(
                ProfileLoader.check_arg_patterns(entry[ARGS], argpats),
                entry[RESULT]
            )

    def test_check_arg_patterns_optional(self):
        for entry in CHECK_ARG_PATTERNS_OPTIONAL:
            argpats = list(map(lambda x: ArgPattern(x), entry[ARGPATTERNS]))
            self.assertEqual(
                ProfileLoader.check_arg_patterns(entry[ARGS], argpats),
                entry[RESULT]
            )

    def test_check_arg_patterns_subcommand(self):
        for entry in CHECK_ARG_PATTERNS_SUBCOMMAND:
            argpats = list(map(lambda x: ArgPattern(x), entry[ARGPATTERNS]))
            self.assertEqual(
                ProfileLoader.check_arg_patterns(entry[ARGS], argpats),
                entry[RESULT]
            )
