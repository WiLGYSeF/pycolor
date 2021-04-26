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

    def color_3bit(light=False):
        colors = [
            'black',
            'red',
            'green',
            'yellow',
            'blue',
            'magenta',
            'cyan',
            'gray'
        ]

        for i in range(2):
            for color in colors:
                print(pyformat.format_string('%%C(%s%s%s) %s %%Cz' % (
                    '^' if i == 1 else '',
                    'light' if light else '',
                    color,
                    color[:3]
                )), end='')
        print(reset)

    print('\n3-bit color palette:')
    color_3bit()
    color_3bit(light=True)

    def color_8bit(background=False):
        for i in range(256):
            print(pyformat.format_string('%%C(%s%d) %3d ' % (
                '^' if background else '',
                i,
                i
            )), end='')
            if (i & 15) == 15:
                print(reset)
        print(reset)

    print('\n8-bit color palette:')
    color_8bit()
    color_8bit(background=True)

    def color_24bit(step, background=False):
        range24 = range(0, 16, step)
        col = 0

        #pylint: disable=invalid-name

        for r in range24:
            rh = _hex(r + (r << 4))
            for g in range24:
                gh = _hex(g + (g << 4))
                for b in range24:
                    bh = _hex(b + (b << 4))
                    rgb = rh + gh + bh
                    print(pyformat.format_string('%%C(%s0x%s) %s ' % (
                        '^' if background else '',
                        rgb,
                        rgb
                    )), end='')

                    col += 1
                    if col == 10:
                        col = 0
                        print(reset)
        print(reset)

    print('\n24-bit color palette sample:')
    color_24bit(3)
    color_24bit(3, background=True)

def _hex(val):
    charset = '0123456789abcdef'
    return charset[val >> 4] + charset[val & 15]
