import argparse
import sys


def get_args(args):
    parser = argparse.ArgumentParser(
        description='do real-time output coloring and formatting of programs',
        usage='%(prog)s [options] COMMAND ARG ...'
    )
    parser.add_argument('--color',
        action='store', default='auto', nargs='?',
        choices=['auto', 'always', 'never', 'on', 'off'],
        help='enable/disable coloring output. if auto is selected, color will be enabled for'
        + ' terminal output but disabled on output redirection. on=always, off=never (default auto)'
    )
    parser.add_argument('--load-file',
        action='append', metavar='FILE', default=[],
        help='use this config file containing profiles'
    )
    parser.add_argument('--profile',
        action='store', metavar='NAME',
        help='specifically use this profile even if it does not match the current arguments'
    )
    parser.add_argument('-t', '--timestamp',
        action='store', metavar='FORMAT', default=False, nargs='?',
        help='force enable "timestamp" for all profiles with an optional FORMAT'
    )
    parser.add_argument('--less',
        action='store', metavar='PATH', default=False, nargs='?',
        help='force enable "less_output" for all profiles with an optional PATH to the less binary'
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

    parser.add_argument('--debug-color',
        action='store_true', default=False,
        help='displays all available color styles and exits'
    )
    parser.add_argument('--debug-format',
        action='store', metavar='FORMAT',
        help='displays the formatted string and exits'
    )

    return parse_known_args(parser, args)

def parse_known_args(parser, args):
    argspace, cmd_args = parser.parse_known_args(args)
    if len(cmd_args) != 0 and cmd_args[0] == '--':
        cmd_args = cmd_args[1:]

    is_consecutive, argidx = consecutive_end_args(args, cmd_args)
    if not is_consecutive:
        argspace = parser.parse_args(args[:argidx])
        cmd_args = args[argidx:]

    if argidx < len(args) and all([
        argidx == 0 or args[argidx - 1] != '--',
        args[argidx].startswith('-'),
    ]):
        parser.print_help()
        sys.exit(1)

    return argspace, cmd_args

def consecutive_end_args(args, subset):
    lenarg = len(args)
    lensub = len(subset)

    if lensub == 0:
        return True, lenarg
    if lenarg < lensub:
        return False, -1

    for i in range(lenarg):
        if args[i] != subset[0]:
            continue

        startidx = i
        off = 1
        i += 1
        while i < lenarg and off < lensub:
            if args[i] != subset[off]:
                return False, startidx
            off += 1
            i += 1
        return i == lenarg and off == lensub, startidx
    return False, lenarg
