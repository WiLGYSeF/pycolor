def update_color_positions(color_positions, pos):
    """Combine the color data with ones from pos

    Args:
        color_positions (dict): The color data
        pos (dict): The new color data to insert to color_positions
    """
    for key, val in pos.items():
        if key not in color_positions:
            color_positions[key] = ''
        color_positions[key] += val

def insert_color_data(data, color_positions, end=-1):
    """Insert colors into the data

    Args:
        data (str): The input data string
        color_positions (dict): The color data
        end (int): Insert colors up to this index

    Returns:
        string: The data with colors inserted
    """
    colored_data = ''
    last = 0

    for key in sorted(color_positions.keys()):
        if end > 0 and key > end:
            return colored_data + data[last:end]
        colored_data += data[last:key] + color_positions[key]
        last = key

    return colored_data + data[last:]

def offset_color_positions(color_positions, offset):
    """Offset all the color data indicies

    Args:
        color_positions (dict): The color data
        offset (int): The offset to add to the color data

    Returns:
        dict: The offsetted color data
    """
    newpos = {}
    for key, val in color_positions.items():
        newpos[key + offset] = val
    return newpos
