import json
import numbers
import re


RETURN_DEFAULT = object()


def build(obj, **kwargs):
    schema = kwargs['schema']
    dest = kwargs.get('dest', {})

    return _build(dest, obj, schema)


def _build(dest, obj, schema, **kwargs):
    name = kwargs.get('name')

    stype = schema.get('type')
    if stype is None:
        if 'enum' in schema:
            return _build_enum(obj, schema, **kwargs)

        raise ValueError('"%s" schema type is not defined: %s' % (name, json.dumps(schema)))

    if not isinstance(stype, list):
        stype = [stype]

    errors = []

    for _ in range(2):
        for typ in stype:
            typ = typ.lower()
            args = kwargs.copy()

            try:
                if typ in ('obj', 'object'):
                    for key, val in schema.get('properties', {}).items():
                        args['name'] = key
                        setattr(dest, key, _build(dest, obj.get(key), val, **args))
                    return dest
                if typ in ('arr', 'array', 'list'):
                    return _build_array(obj, schema, **args)
                if typ in ('bool', 'boolean'):
                    return _build_boolean(obj, schema, **args)
                if typ == 'enum':
                    return _build_enum(obj, schema, **args)
                if typ in ('int', 'integer'):
                    return _build_integer(obj, schema, **args)
                if typ in ('num', 'number'):
                    return _build_number(obj, schema, **args)
                if typ in ('str', 'string'):
                    return _build_string(obj, schema, **args)
                if typ in ('str_arr', 'string_array'):
                    return _build_string_array(obj, schema, **args)
                if typ in ('null', 'none'):
                    if obj is not None:
                        raise ValueError('"%s" is defined and not null: %s' % (name, obj))
                    return None
            except ValueError as ver:
                errors.append(ver)

    raise ValueError(errors)

def _build_array(obj, schema, **kwargs):
    minlen = schema.get('min_length')
    maxlen = schema.get('max_length')

    if obj == RETURN_DEFAULT:
        return []

    if not isinstance(obj, list):
        return _invalid(obj, schema, **kwargs)
    if minlen is not None and len(obj) < minlen:
        return _invalid(obj, schema, **kwargs)
    if maxlen is not None and len(obj) > maxlen:
        return _invalid(obj, schema, **kwargs)

    return obj

    arr = []
    for val in obj:
        print(val, schema)
        raise ValueError()
        # TODO
        #arr.append(_build({}, val, schema))
    return arr

def _build_boolean(obj, schema, **kwargs):
    if obj == RETURN_DEFAULT:
        return False

    if not isinstance(obj, bool):
        return _invalid(obj, schema, **kwargs)
    return obj

def _build_enum(obj, schema, **kwargs):
    values = schema['enum']
    if obj == RETURN_DEFAULT:
        return schema['default'] if 'default' in schema else values[0]
    if obj not in values:
        return _invalid(obj, schema, **kwargs)
    return obj

def _build_integer(obj, schema, **kwargs):
    minval = schema.get('min_value')
    maxval = schema.get('max_value')

    if obj == RETURN_DEFAULT:
        return 0

    if not isinstance(obj, int):
        return _invalid(obj, schema, **kwargs)
    if minval is not None and obj < minval:
        return _invalid(obj, schema, **kwargs)
    if maxval is not None and obj > maxval:
        return _invalid(obj, schema, **kwargs)

    return int(obj)

def _build_number(obj, schema, **kwargs):
    minval = schema.get('min_value')
    maxval = schema.get('max_value')

    if obj == RETURN_DEFAULT:
        return 0.0

    if not isinstance(obj, numbers.Number):
        return _invalid(obj, schema, **kwargs)
    if minval is not None and obj < minval:
        return _invalid(obj, schema, **kwargs)
    if maxval is not None and obj > maxval:
        return _invalid(obj, schema, **kwargs)

    return float(obj)

def _build_string(obj, schema, **kwargs):
    minlen = schema.get('min_length')
    maxlen = schema.get('max_length')
    regex = schema.get('regex')

    if obj == RETURN_DEFAULT:
        return ''

    if not isinstance(obj, str):
        return _invalid(obj, schema, **kwargs)
    if minlen is not None and len(obj) < minlen:
        return _invalid(obj, schema, **kwargs)
    if maxlen is not None and len(obj) > maxlen:
        return _invalid(obj, schema, **kwargs)
    if regex is not None and not re.search(regex, obj):
        return _invalid(obj, schema, **kwargs)

    return str(obj)

def _build_string_array(obj, schema, **kwargs):
    if isinstance(obj, list):
        return _build_string(''.join(obj), schema)
    return _build_string(obj, schema, **kwargs)

def _invalid(obj, schema, **kwargs):
    name = kwargs.get('name')
    require_value = kwargs.get('require_value', False)

    if require_value or obj is not None or schema.get('required', False):
        if obj is not None:
            raise ValueError('"%s" not valid %s: %s' % (name, _get_type(schema), obj))
        raise ValueError('"%s" requires %s value' % (name, _get_type(schema)))

    args = kwargs.copy()
    args['require_value'] = True
    return _build({}, schema.get('default', RETURN_DEFAULT), schema, **args)

def _get_type(schema):
    if 'type' in schema:
        return schema['type']

    if 'enum' in schema:
        return 'enum'
    return None
