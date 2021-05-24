def update_color_positions(color_positions, pos):
    for key, val in pos.items():
        if key not in color_positions:
            color_positions[key] = ''
        color_positions[key] += val

def insert_color_data(data, color_positions, end=-1):
    colored_data = ''
    last = 0

    for key in sorted(color_positions.keys()):
        if end > 0 and key > end:
            return colored_data + data[last:end]
        colored_data += data[last:key] + color_positions[key]
        last = key

    return colored_data + data[last:]

def offset_color_positions(color_positions, offset):
    newpos = {}
    for key, val in color_positions.items():
        newpos[key + offset] = val
    return newpos
