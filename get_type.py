def get_type(obj, key, val_type, default=None):
    result = obj.get(key, default)
    if not isinstance(result, val_type):
        return default
    return result
