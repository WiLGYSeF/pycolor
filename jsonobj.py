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

    if schema is True:
        return obj
    if schema is False:
        raise ValueError('schema is false')

    stype = schema.get('type')
    if stype is None:
        if 'enum' in schema:
            return _build_enum(obj, schema, **kwargs)

        raise ValueError('"%s" schema type is not defined: %s' % (name, json.dumps(schema)))

    if not isinstance(stype, list):
        stype = [stype]

    errors = []

    for typ in stype:
        typ = typ.lower()

        try:
            if typ in ('arr', 'array', 'list'):
                return _build_array(obj, schema, **kwargs)
            if typ in ('bool', 'boolean'):
                return _build_boolean(obj, schema, **kwargs)
            if typ == 'enum':
                return _build_enum(obj, schema, **kwargs)
            if typ in ('int', 'integer'):
                return _build_integer(obj, schema, **kwargs)
            if typ in ('null', 'none'):
                return _build_null(obj, schema, **kwargs)
            if typ in ('num', 'number'):
                return _build_number(obj, schema, **kwargs)
            if typ in ('obj', 'object', 'dict'):
                return _build_object(obj, schema, dest_obj=dest, **kwargs)
            if typ in ('str', 'string'):
                return _build_string(obj, schema, **kwargs)

            if typ in ('str_arr', 'string_array'):
                return _build_string_array(obj, schema, **kwargs)
        except ValueError as ver:
            errors.append(ver)

    raise ValueError(errors)

def _build_array(obj, schema, **kwargs):
    minlen = schema.get('minItems')
    maxlen = schema.get('maxItems')
    unique = schema.get('uniqueItems')

    if obj == RETURN_DEFAULT:
        return []

    arr = []

    if not isinstance(obj, list):
        return _invalid(obj, schema, **kwargs)
    if minlen is not None and len(obj) < minlen:
        return _invalid(obj, schema, **kwargs)
    if maxlen is not None and len(obj) > maxlen:
        return _invalid(obj, schema, **kwargs)

    for itm in obj:
        arr.append(itm)

    if unique:
        itemset = set()
        for itm in arr:
            if itm in itemset:
                raise ValueError()
            itemset.add(itm)

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
    if obj == RETURN_DEFAULT:
        return 0

    if not isinstance(obj, int):
        return _invalid(obj, schema, **kwargs)

    return int(_build_number(obj, schema, **kwargs))

def _build_null(obj, schema, **kwargs):
    if obj is not None:
        name = kwargs.get('name')
        raise ValueError('"%s" is defined and not null: %s' % (name, obj))
    return None

def _build_number(obj, schema, **kwargs):
    minval = schema.get('minimum')
    maxval = schema.get('maximum')
    exclminval = schema.get('exclusiveMinimum')
    exclmaxval = schema.get('exclusiveMaximum')
    multiple_of = schema.get('multipleOf')

    if obj == RETURN_DEFAULT:
        return 0.0

    if not isinstance(obj, numbers.Number):
        return _invalid(obj, schema, **kwargs)
    if minval is not None and obj < minval:
        return _invalid(obj, schema, **kwargs)
    if maxval is not None and obj > maxval:
        return _invalid(obj, schema, **kwargs)
    if exclminval is not None and obj <= exclminval:
        return _invalid(obj, schema, **kwargs)
    if exclmaxval is not None and obj >= exclmaxval:
        return _invalid(obj, schema, **kwargs)
    if multiple_of is not None and obj % multiple_of != 0:
        return _invalid(obj, schema, **kwargs)

    return float(obj)

def _build_object(obj, schema, **kwargs):
    dest = kwargs['dest_obj']

    if 'properties' in schema:
        args = kwargs.copy()
        del args['dest_obj']

        for key, val in schema['properties'].items():
            args['name'] = key
            setattr(dest, key, _build({}, obj.get(key), val, **args))
        return dest

    if not isinstance(obj, dict):
        return _invalid(obj, schema, **kwargs)
    return obj

def _build_string(obj, schema, **kwargs):
    minlen = schema.get('minLength')
    maxlen = schema.get('maxLength')
    regex = schema.get('pattern')
    format_type = schema.get('format')

    if obj == RETURN_DEFAULT:
        return ''

    if format_type is not None:
        raise ValueError()

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
        return _build_string(''.join(obj), schema, **kwargs)
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
