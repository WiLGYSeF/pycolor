def get_type(obj, val, val_type, default=None):
    result = obj.get(val, default)
    if not isinstance(result, val_type):
        return default
    return result
