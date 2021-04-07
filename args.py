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
