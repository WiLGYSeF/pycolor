# based on: https://json-schema.org/

from numbers import Number
import re


RETURN_DEFAULT = object()

class ValidationError(Exception):
    def __init__(self, schema, message):
        self.schema = schema
        self.message = message
        super().__init__(self.message)


def build(obj, **kwargs):
    schema = kwargs['schema']
    dest = kwargs.get('dest', {})

    result = _build(obj, schema)
    if schema.get('type') == 'object':
        if isinstance(dest, object):
            for key, val in result.items():
                setattr(dest, key, val)
        else:
            for key, val in result.items():
                dest[key] = val
    return result

def _build(obj, schema, **kwargs):
    name = kwargs.get('name')

    if schema is True:
        return obj
    if schema is False:
        raise ValidationError(schema, 'schema is false')

    stype = getval(schema, 'type', (str, list))
    if stype is None:
        if 'enum' in schema:
            return _build_enum(obj, schema, **kwargs)
        if 'const' in schema:
            return _build_const(obj, schema, **kwargs)

        raise ValidationError(schema, '"%s" schema type is not defined' % name)

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
            if typ == 'const':
                return _build_const(obj, schema, **kwargs)
            if typ == 'enum':
                return _build_enum(obj, schema, **kwargs)
            if typ in ('int', 'integer'):
                return _build_integer(obj, schema, **kwargs)
            if typ in ('null', 'none'):
                return _build_null(obj, schema, **kwargs)
            if typ in ('num', 'number'):
                return _build_number(obj, schema, **kwargs)
            if typ in ('obj', 'object', 'dict'):
                return _build_object(obj, schema, **kwargs)
            if typ in ('str', 'string'):
                return _build_string(obj, schema, **kwargs)

            if typ in ('str_arr', 'string_array'):
                return _build_string_array(obj, schema, **kwargs)
        except ValidationError as ver:
            errors.append(ver)

    raise ValidationError(schema, errors)

def _build_array(obj, schema, **kwargs):
    items = getval(schema, 'items', (dict, list))
    contains = getval(schema, 'contains', dict)
    additional_items = getval(schema, 'additionalItems', bool, True)
    minlen = getval(schema, 'minItems', int)
    maxlen = getval(schema, 'maxItems', int)
    unique = getval(schema, 'uniqueItems', bool, False)

    if obj == RETURN_DEFAULT:
        return []

    arr = []

    if not isinstance(obj, list):
        return _invalid(obj, schema, **kwargs)
    if minlen is not None and len(obj) < minlen:
        return _invalid(obj, schema, **kwargs)
    if maxlen is not None and len(obj) > maxlen:
        return _invalid(obj, schema, **kwargs)

    if items is not None:
        if isinstance(items, dict):
            for itm in obj:
                args = kwargs.copy()
                args['require_value'] = True
                arr.append(_build(itm, items, **args))
        elif isinstance(items, list):
            if not additional_items and len(items) != len(obj):
                raise ValidationError(schema, '')
            if len(obj) < len(items):
                raise ValidationError(schema, '')

            for i in range(len(items)): #pylint: disable=consider-using-enumerate
                args = kwargs.copy()
                args['require_value'] = True
                arr.append(_build(obj[i], items[i], **args))

            for i in range(len(items), len(obj)):
                if isinstance(additional_items, dict):
                    args = kwargs.copy()
                    args['require_value'] = True
                    arr.append(_build(obj[i], additional_items, **args))
                else:
                    arr.append(obj[i])
    elif contains is not None:
        matches = 0
        for i in range(len(items)):
            try:
                args = kwargs.copy()
                args['require_value'] = True
                arr.append(_build(obj[i], contains, **args))
                matches += 1
            except ValidationError:
                arr.append(obj[i])

        if matches == 0:
            raise ValidationError(schema, '')
    else:
        for itm in obj:
            arr.append(itm)

    if unique:
        itemset = set()
        for itm in arr:
            if itm in itemset:
                raise ValidationError(schema, 'array contains duplicate items')
            itemset.add(itm)

    return arr

def _build_boolean(obj, schema, **kwargs):
    if obj == RETURN_DEFAULT:
        return False

    if not isinstance(obj, bool):
        return _invalid(obj, schema, **kwargs)
    return obj

def _build_const(obj, schema, **kwargs):
    value = schema['const']
    if obj == RETURN_DEFAULT:
        return value
    if obj != value:
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
        raise ValidationError(schema, '"%s" is defined and not null: %s' % (name, obj))
    return None

def _build_number(obj, schema, **kwargs):
    minval = getval(schema, 'minimum', Number)
    maxval = getval(schema, 'maximum', Number)
    exclminval = getval(schema, 'exclusiveMinimum', Number)
    exclmaxval = getval(schema, 'exclusiveMaximum', Number)
    multiple_of = getval(schema, 'multipleOf', Number)

    if obj == RETURN_DEFAULT:
        return 0.0

    if not isinstance(obj, Number):
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
    properties = getval(schema, 'properties', dict)
    additional_properties = getval(schema, 'additionalProperties', (dict, bool), True)
    required = getval(schema, 'required', list, [])
    property_names = getval(schema, 'propertyNames', dict)
    minlen = getval(schema, 'minProperties', int)
    maxlen = getval(schema, 'maxProperties', int)
    dependencies = getval(schema, 'dependencies', dict, {})
    pattern_properties = getval(schema, 'patternProperties', dict)

    newobj = {}

    if not isinstance(obj, dict):
        return _invalid(obj, schema, **kwargs)
    if minlen is not None and len(obj) < minlen:
        return _invalid(obj, schema, **kwargs)
    if maxlen is not None and len(obj) > maxlen:
        return _invalid(obj, schema, **kwargs)

    if properties is not None:
        args = kwargs.copy()

        for key, val in obj.items():
            if key in properties:
                args['name'] = key
                newobj[key] = _build(val, properties[key], **args)
            else:
                if isinstance(additional_properties, dict):
                    newobj[key] = _build(val, additional_properties, **args)
                else:
                    if additional_properties is False:
                        raise ValidationError(schema, 'additonal properties not allowed')
                    newobj[key] = val

        for key, val in properties.items():
            if key not in newobj:
                newobj[key] =  val.get('default', _build(None, val, **args))
    else:
        for key, val in obj.items():
            newobj[key] = val

    for req in required:
        if req not in newobj:
            raise ValidationError(schema,'missing required property: "%s"' % req)

    for key, dep in dependencies.items():
        if key not in newobj:
            continue
        if isinstance(dep, list):
            for val in dep:
                if val not in newobj:
                    raise ValidationError(schema,
                        'missing dependency for "%s": "%s"' % (key, val)
                    )
        elif isinstance(dep, dict):
            _build(obj, dep, **kwargs)

    return newobj

def _build_string(obj, schema, **kwargs):
    minlen = getval(schema, 'minLength', int)
    maxlen = getval(schema, 'maxLength', int)
    regex = getval(schema, 'pattern', str)
    format_type = getval(schema, 'format', str)

    if obj == RETURN_DEFAULT:
        return ''

    if format_type is not None:
        raise ValidationError(schema, 'not yet implemented')

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

    # TODO
    if require_value or obj is not None or schema.get('required', False):
        if obj is not None:
            raise ValidationError(schema, '"%s" not valid %s: %s' % (name, _get_type(schema), obj))
        raise ValidationError(schema, '"%s" requires %s value' % (name, _get_type(schema)))

    args = kwargs.copy()
    args['require_value'] = True
    return _build(schema.get('default', RETURN_DEFAULT), schema, **args)

def _get_type(schema):
    if 'type' in schema:
        return schema['type']

    if 'enum' in schema:
        return 'enum'
    return None

def getval(obj, key, expected_type, default=None, has_default=True):
    if key not in obj:
        if not has_default:
            raise ValueError()
        return default

    val = obj[key]
    if not isinstance(val, expected_type):
        raise ValueError()
    return val
