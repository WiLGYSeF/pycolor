import sys

from pycolor_class import Pycolor


PYCOLOR_CONFIG_FNAME = 'config.json'


def main():
    my_args, cmd_args = get_my_args(sys.argv)
    if len(cmd_args) == 0:
        print('no command')
        exit(1)

    pycobj = Pycolor()
    load_files = []
    profile_name = None

    for arg in my_args:
        if arg.startswith('--color'):
            _, argval = get_arg(arg, 'auto')
            pycobj.color_mode = argval
        elif arg.startswith('--load-file'):
            _, argval = get_arg(arg)
            if argval is None:
                raise Exception()
            load_files.append(argval)
        elif arg.startswith('--profile'):
            _, argval = get_arg(arg)
            if argval is None:
                raise Exception()
            profile_name = argval

    pycobj.load_file(PYCOLOR_CONFIG_FNAME)

    for fname in load_files:
        pycobj.load_file(fname)

    profile = None
    if profile_name is not None:
        profile = pycobj.get_profile_by_name(profile_name)

    returncode = pycobj.execute(cmd_args, profile=profile)
    sys.exit(returncode)

def get_my_args(argv, start_idx=1):
    my_args = []
    cmd_args = []

    idx = start_idx
    while idx < len(argv):
        arg = argv[idx]
        if arg == '--':
            idx += 1
            break
        if not arg.startswith('--'):
            break

        my_args.append(arg)
        idx += 1

    while idx < len(argv):
        cmd_args.append(argv[idx])
        idx += 1

    return my_args, cmd_args

def get_arg(string, default=None):
    if not string.startswith('--'):
        raise ValueError()

    idx = string.find('=')
    if idx == -1:
        return string[2:], default

    return string[2:idx], string[idx + 1:]
