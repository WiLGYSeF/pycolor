import typing

from ....strman.search_replace import ReplaceRange
from . import ColorPositions
from .color import ANSI_REGEX

def update_color_positions(
    color_positions: ColorPositions,
    pos: ColorPositions
) -> None:
    """Combine the color data with ones from pos

    Args:
        color_positions (dict): The color data
        pos (dict): The new color data to insert to color_positions
    """
    for key, val in pos.items():
        if key not in color_positions:
            color_positions[key] = ''
        color_positions[key] += val

def insert_color_data(
    data: str,
    color_positions: ColorPositions,
    end: int = -1
) -> str:
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

def extract_color_data(data: str) -> typing.Tuple[str, ColorPositions]:
    """Extracts ANSI color data from string

    Args:
        data (str): String with ANSI colors

    Returns:
        tuple: String without ANSI colors, and extracted colors
    """
    result = ''
    color_positions: ColorPositions = {}
    last = 0

    for match in ANSI_REGEX.finditer(data):
        result += data[last:match.start()]

        length = len(result)
        if length not in color_positions:
            color_positions[length] = ''
        color_positions[length] += match.group(0)

        last = match.end()
    result += data[last:]

    return result, color_positions

def update_color_positions_replace_ranges(
    color_positions: ColorPositions,
    replace_ranges: typing.List[ReplaceRange]
) -> ColorPositions:
    """Update color positions based on replace ranges

    Args:
        color_positions (dict): Color positions
        replace_ranges (list): Replace ranges

    Returns:
        dict: Color positions with updated positions
    """
    positions: ColorPositions = {}
    offset = 0
    replace_idx = 0

    replace_ranges.sort(key=lambda x: x[0][0])

    for key, val in color_positions.items():
        set_val = True
        while replace_idx < len(replace_ranges):
            oldrange, newrange = replace_ranges[replace_idx]
            if key > oldrange[1]:
                offset += newrange[1] - oldrange[1] - (newrange[0] - oldrange[0])
                replace_idx += 1
            elif oldrange[0] < key and key <= oldrange[1]:
                set_val = False
                break
            else:
                break
        if set_val:
            positions[key + offset] = val
    return positions

def offset_color_positions(
    color_positions: ColorPositions,
    offset: int
) -> ColorPositions:
    """Offset all the color data indicies inplace

    Args:
        color_positions (dict): The color data
        offset (int): The offset to add to the color data

    Returns:
        dict: color_positions
    """
    if offset == 0:
        return color_positions

    for key in sorted(color_positions.keys(), reverse=True):
        color_positions[key + offset] = color_positions[key]
        del color_positions[key]
    return color_positions
