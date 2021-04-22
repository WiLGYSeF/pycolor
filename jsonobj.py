import json
import numbers
import re


RETURN_DEFAULT = object()

def build(obj, **kwargs):
    schema = kwargs['schema']
    dest = kwargs.get('dest', {})

    return _build(dest, obj, schema)


def _build(dest, obj, schema):
    stype = schema.get('type')
    if stype is None:
        if 'enum' in schema:
            return _build_enum(obj, schema)

        raise ValueError('schema type is not defined: %s' % json.dumps(schema))

    if not isinstance(stype, list):
        stype = [stype]

    for typ in stype:
        typ = typ.lower()

        try:
            if typ in ('obj', 'object'):
                for key, val in schema.get('properties', {}).items():
                    setattr(dest, key, _build(dest, obj.get(key), val))
                return dest
            if typ in ('arr', 'array'):
                return _build_array(obj, schema)
            if typ in ('bool', 'boolean'):
                return _build_boolean(obj, schema)
            if typ == 'enum':
                return _build_enum(obj, schema)
            if typ in ('int', 'integer'):
                return _build_integer(obj, schema)
            if typ in ('num', 'number'):
                return _build_number(obj, schema)
            if typ in ('str', 'string'):
                return _build_string(obj, schema)
            if typ in ('null', 'none'):
                if obj is not None:
                    raise ValueError('value is defined and not null: %s' % obj)
                return None
        except ValueError:
            pass

    raise ValueError()

def _build_array(obj, schema):
    minlen = schema.get('min_length')
    maxlen = schema.get('max_length')

    if obj == RETURN_DEFAULT:
        return []

    if not isinstance(obj, list):
        return _invalid(obj, schema)
    if minlen is not None and len(obj) < minlen:
        return _invalid(obj, schema)
    if maxlen is not None and len(obj) > maxlen:
        return _invalid(obj, schema)

    arr = []
    for val in obj:
        raise ValueError()
        # TODO
        #arr.append(_build({}, val, schema))
    return arr

def _build_boolean(obj, schema):
    if obj == RETURN_DEFAULT:
        return False

    if not isinstance(obj, bool):
        return _invalid(obj, schema)
    return obj

def _build_enum(obj, schema):
    values = schema['enum']
    if obj == RETURN_DEFAULT:
        return values[0]
    if obj not in values:
        return _invalid(obj, schema)
    return obj

def _build_integer(obj, schema):
    minval = schema.get('min_value')
    maxval = schema.get('max_value')

    if obj == RETURN_DEFAULT:
        return 0

    if not isinstance(obj, int):
        return _invalid(obj, schema)
    if minval is not None and obj < minval:
        return _invalid(obj, schema)
    if maxval is not None and obj > maxval:
        return _invalid(obj, schema)

    return int(obj)

def _build_number(obj, schema):
    minval = schema.get('min_value')
    maxval = schema.get('max_value')

    if obj == RETURN_DEFAULT:
        return 0.0

    if not isinstance(obj, numbers.Number):
        return _invalid(obj, schema)
    if minval is not None and obj < minval:
        return _invalid(obj, schema)
    if maxval is not None and obj > maxval:
        return _invalid(obj, schema)

    return float(obj)

def _build_string(obj, schema):
    minlen = schema.get('min_length')
    maxlen = schema.get('max_length')
    regex = schema.get('regex')

    if obj == RETURN_DEFAULT:
        return ''

    if not isinstance(obj, str):
        return _invalid(obj, schema)
    if minlen is not None and len(obj) < minlen:
        return _invalid(obj, schema)
    if maxlen is not None and len(obj) > maxlen:
        return _invalid(obj, schema)
    if regex is not None and not re.search(regex, obj):
        return _invalid(obj, schema)

    return str(obj)

def _invalid(obj, schema):
    if obj is not None or schema.get('required', False):
        raise ValueError('value is not valid')

    subschema = dictcopy(schema)
    subschema['required'] = True
    return _build({}, schema.get('default', RETURN_DEFAULT), subschema)

def dictcopy(dct):
    copy = {}
    for key, val in dct.items():
        if isinstance(val, dict):
            copy[key] = dictcopy(val)
        else:
            copy[key] = val
    return copy
