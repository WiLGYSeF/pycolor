import pyformat


def debug_colors():
    reset = pyformat.format_string('%Cz')

    print('styles:')
    for style in [
        'nor',
        'bol',
        'dim',
        'ita',
        'und',
        'bli',
        'inv',
        'hid',
        'str',
        'ove',
    ]:
        print(pyformat.format_string('%%C(%s) %s %%Cz' % (style, style)), end='')
    print(reset)

    print('\n8-bit color:')
    for i in range(256):
        print(pyformat.format_string('%%C(%d) %3d ' % (i, i)), end='')
        if (i & 15) == 15:
            print()
    for i in range(256):
        print(pyformat.format_string('%%C(^%d) %3d ' % (i, i)), end='')
        if (i & 15) == 15:
            print()
    print(reset)

    """
    print('\n24-bit color:')
    for r in range(256):
        rh = _hex(r)
        for g in range(256):
            gh = _hex(g)
            for b in range(256):
                bh = _hex(b)
                rgb = rh + gh + bh
                print(pyformat.format_string('%%C(0x%s) %s ' % (rgb, rgb)), end='')
                if (b & 15) == 15:
                    print()
    print(reset)
    """
"""
def _hex(val):
    charset = '0123456789abcdef'
    return charset[val >> 4] + charset[val & 15]
"""
