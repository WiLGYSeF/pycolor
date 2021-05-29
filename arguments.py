import argparse
import sys


def get_args(args):
    parser = argparse.ArgumentParser(
        description='do real-time output coloring and formatting for commands',
        usage='%(prog)s [options] COMMAND ARG ...'
    )
    parser.add_argument('--color',
        action='store', default='auto', nargs='?',
        choices=['auto', 'always', 'never', 'on', 'off'],
        help='enable/disable coloring output. if set to auto, color will be enabled for'
        + ' terminal output but disabled on output redirection (default auto)'
    )
    parser.add_argument('--load-file',
        action='append', metavar='FILE', default=[],
        help='use this config file containing profiles'
    )
    parser.add_argument('-p', '--profile',
        action='store', metavar='NAME',
        help='specifically use this profile even if it does not match the current arguments'
    )
    parser.add_argument('-t', '--timestamp',
        action='store', metavar='FORMAT', default=False, nargs='?',
        help='force enable "timestamp" for all profiles with an optional FORMAT'
    )
    parser.add_argument('--less',
        action='store_true', default=False,
        help='force enable "less_output" for all profiles'
    )
    parser.add_argument('-v', '--verbose',
        action='count', default=0,
        help='enable debug mode to assist in configuring profiles'
    )
    parser.add_argument('--execv',
        action='store_true', default=True,
        help='use execv() if no profile matches the given command (default)'
    )
    parser.add_argument('--no-execv',
        dest='execv', action='store_false',
        help='do not use execv() if no profile matches the given command'
    )
    parser.add_argument('--tty',
        action='store_true', default=False,
        help='run the command in a pseudo-terminal'
    )
    parser.add_argument('--no-tty',
        dest='tty', action='store_false',
        help='do not run the command in a pseudo-terminal (default)'
    )
    parser.add_argument('-i', '--interactive',
        action='store_true', default=False,
        help='force enable "interactive" for all profiles'
    )

    parser.add_argument('--debug-color',
        action='store_true', default=False,
        help='displays all available color styles and exits'
    )
    parser.add_argument('--debug-format',
        action='store', metavar='FORMAT',
        help='displays the formatted string and exits'
    )
    parser.add_argument('--debug-from-stdin',
        action='store_true', default=False,
        help='reads stdin instead of running the given command'
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--debug-log',
        action='store', metavar='FILE',
        help='write debug messages to a file instead of stdout'
    )
    group.add_argument('--debug-log-out',
        action='store', metavar='FILE',
        help='write debug messages to a file in addition to stdout'
    )

    return parse_known_args(parser, args)

def parse_known_args(parser, args):
    # TODO: using parser._actions is somewhat of a hack
    args, cmd_args = split_args(args, parser._actions)
    argspace = parser.parse_args(args)
    return argspace, cmd_args

def split_args(args, actions):
    action_nargs = {}

    for action in actions:
        for opt in action.option_strings:
            action_nargs[opt] = action.nargs

    last_arg = None
    idx = 0

    while idx < len(args):
        arg = args[idx]
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
            # TODO: this depends on the action
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
