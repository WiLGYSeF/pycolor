import re


def build(obj, **kwargs):
    schema = kwargs['schema']
    dest = kwargs.get('dest', {})

    return _build(dest, obj, schema)


def _build(dest, obj, schema):
    stype = schema.get('type')
    if stype in ('obj', 'object'):
        for key, val in schema.get('properties', {}).items():
            setattr(dest, key, _build(dest, obj.get(key), val))
        return dest
    if stype in ('bool', 'boolean'):
        return _build_boolean(obj, schema)
    if stype in ('str', 'string'):
        return _build_string(obj, schema)
    if stype in ('arr', 'array'):
        return _build_array(obj, schema)
    if stype in ('int', 'integer'):
        return _build_integer(obj, schema)
    if stype in ('num', 'number'):
        return _build_number(obj, schema)
    if stype == 'enum':
        return _build_enum(obj, schema)

    if 'enum' in schema:
        return _build_enum(obj, schema)

    raise ValueError()

def _build_boolean(obj, schema):
    values = {
        '1': True,
        't': True,
        'true': True,
        '0': False,
        'f': False,
        'false': False
    }

    val = values.get(str(obj).lower())
    if val is None:
        return _invalid(obj, schema)
    return val

def _build_string(obj, schema):
    minlen = schema.get('min_length')
    maxlen = schema.get('max_length')
    regex = schema.get('regex')

    if minlen is not None and len(obj) < minlen:
        return _invalid(obj, schema)
    if maxlen is not None and len(obj) > maxlen:
        return _invalid(obj, schema)
    if regex is not None and not re.search(regex, obj):
        return _invalid(obj, schema)

    return str(obj)

def _build_array(obj, schema):
    minlen = schema.get('min_length')
    maxlen = schema.get('max_length')

    if not isinstance(obj, list):
        return _invalid(obj, schema)

    if minlen is not None and len(obj) < minlen:
        return _invalid(obj, schema)
    if maxlen is not None and len(obj) > maxlen:
        return _invalid(obj, schema)

    arr = []
    for val in obj:
        # TODO
        #arr.append(build({}, val, schema))
        pass
    return arr

def _build_integer(obj, schema):
    minval = schema.get('min_value')
    maxval = schema.get('max_value')

    if minval is not None and obj < minval:
        return _invalid(obj, schema)
    if maxval is not None and obj > maxval:
        return _invalid(obj, schema)

    return int(obj)

def _build_number(obj, schema):
    minval = schema.get('min_value')
    maxval = schema.get('max_value')

    if minval is not None and obj < minval:
        return _invalid(obj, schema)
    if maxval is not None and obj > maxval:
        return _invalid(obj, schema)

    return float(obj)

def _build_enum(obj, schema):
    values = schema['enum']
    if obj not in values:
        return _invalid(obj, schema)
    return obj

def _invalid(obj, schema):
    if 'default' not in schema:
        raise ValueError()

    subschema = dictcopy(schema)
    del subschema['default']
    return _build({}, schema['default'], subschema)

def dictcopy(dct):
    copy = {}
    for key, val in dct.items():
        if isinstance(val, dict):
            copy[key] = dictcopy(val)
        else:
            copy[key] = val
    return copy
