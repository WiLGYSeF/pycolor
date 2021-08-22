import argparse


# TODO: messy global
_parser = None


def _build_parser():
    global _parser
    _parser = argparse.ArgumentParser(
        description='do real-time output coloring and formatting for commands',
        usage='%(prog)s [options] COMMAND ARG ...'
    )
    _parser.add_argument('-V', '--version',
        action='store_true', default=False,
        help='prints the version and exits'
    )
    _parser.add_argument('--color',
        action='store', default='auto', nargs='?',
        choices=['auto', 'always', 'never', 'on', 'off'],
        help='enable/disable coloring output. if set to auto, color will be enabled for'
        + ' terminal output but disabled on output redirection (default auto)'
    )
    _parser.add_argument('--load-file',
        action='append', metavar='FILE', default=[],
        help='use this config file containing profiles'
    )
    _parser.add_argument('-p', '--profile',
        action='store', metavar='NAME',
        help='specifically use this profile even if it does not match the current arguments'
    )
    _parser.add_argument('-v', '--verbose',
        action='count', default=0,
        help='enable debug mode to assist in configuring profiles'
    )
    _parser.add_argument('--execv',
        action='store_true', default=True,
        help='use execv() if no profile matches the given command (default)'
    )
    _parser.add_argument('--no-execv',
        dest='execv', action='store_false',
        help='do not use execv() if no profile matches the given command'
    )
    _parser.add_argument('--stdin',
        action='store_true', default=False,
        help='reads from stdin instead of running the given command. '
        + 'the command can still be given to let pycolor know which profile it should use'
    )

    group = _parser.add_argument_group('profile options')
    group.add_argument('-t', '--timestamp',
        action='store', metavar='FORMAT', default=False, nargs='?',
        help='force enable "timestamp" for all profiles with an optional FORMAT'
    )
    group.add_argument('--tty',
        action='store_true', default=False,
        help='run the command in a pseudo-terminal'
    )
    group.add_argument('--no-tty',
        dest='tty', action='store_false',
        help='do not run the command in a pseudo-terminal (default)'
    )
    group.add_argument('-i', '--interactive',
        action='store_true', default=False,
        help='force enable "interactive" for all profiles'
    )

    group = _parser.add_argument_group('debug options')
    group.add_argument('--debug-color',
        action='store_true', default=False,
        help='display all available color styles and exit'
    )
    group.add_argument('-f', '--debug-format',
        action=DebugFormatAction, metavar='FORMAT',
        help='display the formatted string and exit, using the long form will ensure that'
        + ' the ANSI colors will be reset afterwards'
    )

    group = group.add_mutually_exclusive_group()
    group.add_argument('--debug-log',
        action='store', metavar='FILE',
        help='write debug messages to a file instead of stdout'
    )
    group.add_argument('--debug-log-out',
        action='store', metavar='FILE',
        help='write debug messages to a file in addition to stdout'
    )

class DebugFormatAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, 'debug_format_reset', option_string == '--debug-format')
        setattr(namespace, self.dest, values)

def get_args(args):
    global _parser
    if _parser is None:
        _build_parser()
    return parse_known_args(_parser, args)

def parse_known_args(parser, args):
    # TODO: using parser._actions is somewhat of a hack
    args, cmd_args = split_args(args, parser._actions)
    argspace = parser.parse_args(args)
    return argspace, cmd_args

def split_args(args, actions):
    """Splits the arguments between ones that belong to pycolor and the command

    Args:
        args (list): The program arguments
        actions (list): The argument actions recognized by the argument parser

    Returns:
        tuple: the arguments split into two lists
    """
    action_nargs = {}

    for action in actions:
        for opt in action.option_strings:
            action_nargs[opt] = action.nargs

    last_arg = None
    idx = 0

    while idx < len(args):
        arg = args[idx]
        if len(arg) == 0:
            idx += 1
            continue
        if arg == '--':
            break
        if arg[0] == '-':
            last_arg = arg
            idx += 1
            continue

        if last_arg not in action_nargs:
            break

        nargs = action_nargs[last_arg]
        if nargs is None:
            # TODO: this depends on the action, but is usually 1
            idx += 1
        elif isinstance(nargs, int):
            while nargs > 0 and idx < len(args) and args[idx][0] != '-':
                nargs -= 1
                idx += 1
            if nargs != 0:
                break
        elif nargs == '?':
            if idx < len(args) and args[idx][0] != '-':
                idx += 1
        elif nargs in ('*', '+'):
            while idx < len(args) and args[idx][0] != '-':
                idx += 1
        else:
            raise ValueError(nargs)
        last_arg = None

    if idx < len(args) and args[idx] == '--':
        return args[:idx], args[idx + 1:]
    return args[:idx], args[idx:]
