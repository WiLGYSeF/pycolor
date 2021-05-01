# based on: https://json-schema.org/

# TODO: string_array is not json-schema

# TODO: https://json-schema.org/understanding-json-schema/structuring.html
# TODO: https://json-schema.org/understanding-json-schema/reference/combining.html

from numbers import Number
import re


RETURN_DEFAULT = object()


class ValidationError(Exception):
    def __init__(self, schema, name, message):
        self.schema = schema
        self.name = name
        self.message = message

        if self.name is not None:
            err = '"%s": %s' % (self.name, self.message)
        else:
            err = self.message

        super().__init__(err)

def build(obj, **kwargs):
    schema = kwargs['schema']
    dest = kwargs.get('dest', {})

    result = _build(obj, schema, root_schema=schema)
    if isinstance(result, Exception):
        raise result

    if schema.get('type') == 'object':
        if isinstance(dest, dict):
            for key, val in result.items():
                dest[key] = val
        else:
            for key, val in result.items():
                setattr(dest, key, val)
    return result

def getval(obj, key, expected_type, default=None, has_default=True):
    if key not in obj:
        if not has_default:
            raise ValueError()
        return default

    val = obj[key]
    if not isinstance(val, expected_type):
        raise ValueError()
    return val

def _build(obj, schema, **kwargs):
    name = kwargs.get('name')

    if isinstance(schema, dict) and '$ref' in schema:
        schema = _get_ref(kwargs['root_schema'], schema['$ref'])

    if schema is True:
        return obj
    if schema is False:
        return ValidationError(schema, name, 'schema is false')
    if not isinstance(schema, dict):
        raise ValueError('schema must be an object')

    stype = getval(schema, 'type', (str, list))
    if stype is None:
        if 'const' in schema:
            stype = 'const'
        if 'properties' in schema:
            stype = 'object'
    if 'enum' in schema:
        stype = 'enum'

    if stype is None:
        return ValidationError(schema, name, 'type is not defined')

    if not isinstance(stype, list):
        stype = [stype]

    errors = []

    for typ in stype:
        result = _build_from_type(obj, schema, typ, **kwargs)
        if not isinstance(result, Exception):
            return result
        errors.append(result)

    if obj is not None and len(errors) != 0:
        return ValidationError(schema, name, str(errors))
    return _build_from_type(
        schema.get('default', RETURN_DEFAULT),
        schema,
        stype[0],
        **kwargs
    )

def _get_ref(root, path):
    idx = path.find('#/')
    if idx == -1:
        raise ValueError('invalid $ref path: %s' % path)
    if idx > 0:
        raise ValueError('not yet implemented')

    parts = path[idx + 2:].split('/')
    schema = root

    for part in parts:
        schema = schema[part]
    return schema

def _build_from_type(obj, schema, type_name, **kwargs):
    func = _buildtbl.get(type_name.lower())
    if func is None:
        return ValueError('invalid schema type: %s' % type_name)
    return func(obj, schema, **kwargs)

def _build_array(obj, schema, **kwargs):
    name = kwargs.get('name')

    items = getval(schema, 'items', (dict, list))
    contains = getval(schema, 'contains', dict)
    additional_items = getval(schema, 'additionalItems', (bool, dict), True)
    minlen = getval(schema, 'minItems', int)
    maxlen = getval(schema, 'maxItems', int)
    unique = getval(schema, 'uniqueItems', bool, False)

    if obj == RETURN_DEFAULT:
        return []

    if not isinstance(obj, list):
        return ValidationError(schema, name, 'not a list')
    if minlen is not None and len(obj) < minlen:
        return ValidationError(schema, name, 'less than minItems')
    if maxlen is not None and len(obj) > maxlen:
        return ValidationError(schema, name, 'greater than maxItems')

    if items is not None:
        if isinstance(items, dict):
            for i in range(len(obj)): #pylint: disable=consider-using-enumerate
                result = _build(obj[i], items, **kwargs)
                if isinstance(result, Exception):
                    return result
                obj[i] = result

        elif isinstance(items, list):
            if additional_items is False and len(items) != len(obj):
                return ValidationError(schema, name, 'cannot have additional items')
            if len(obj) < len(items):
                return ValidationError(schema, name, 'list is too short')

            for i in range(len(items)): #pylint: disable=consider-using-enumerate
                result = _build(obj[i], items[i], **kwargs)
                if isinstance(result, Exception):
                    return result
                obj[i] = result

            if isinstance(additional_items, dict):
                for i in range(len(items), len(obj)):
                    result = _build(obj[i], additional_items, **kwargs)
                    if isinstance(result, Exception):
                        return result
                    obj[i] = result
    elif contains is not None:
        matches = 0
        for i in range(len(obj)): #pylint: disable=consider-using-enumerate
            result = _build(obj[i], contains, **kwargs)
            if not isinstance(result, Exception):
                obj[i] = result
                matches += 1

        if matches == 0:
            return ValidationError(schema, name, 'contains does not match any item')

    if unique:
        itemset = set()
        for itm in obj:
            if itm in itemset:
                return ValidationError(schema, name, 'contains duplicate items')
            itemset.add(itm)

    return obj

def _build_boolean(obj, schema, **kwargs):
    name = kwargs.get('name')

    if obj == RETURN_DEFAULT:
        return False

    if not isinstance(obj, bool):
        return ValidationError(schema, name, 'not a boolean')
    return obj

def _build_const(obj, schema, **kwargs):
    value = schema['const']
    if obj == RETURN_DEFAULT:
        return value
    if obj != value:
        name = kwargs.get('name')
        return ValidationError(schema, name, 'not const value')
    return obj

def _build_enum(obj, schema, **kwargs):
    name = kwargs.get('name')

    values = schema['enum']
    if obj == RETURN_DEFAULT:
        obj = values[0]
    elif obj not in values:
        return ValidationError(schema, name, 'not an enum value')

    if 'type' in schema and schema['type'] != 'enum':
        return _build(obj, {'type': schema['type']}, **kwargs)
    return obj

def _build_integer(obj, schema, **kwargs):
    name = kwargs.get('name')

    if obj == RETURN_DEFAULT:
        return 0

    if not isinstance(obj, int):
        return ValidationError(schema, name, 'not an integer')

    val = _build_number(obj, schema, **kwargs)
    return int(val) if isinstance(val, Number) else val

def _build_null(obj, schema, **kwargs):
    if obj == RETURN_DEFAULT:
        return None

    if obj is not None:
        name = kwargs.get('name')
        return ValidationError(schema, name, 'is not null')
    return None

def _build_number(obj, schema, **kwargs):
    name = kwargs.get('name')

    minval = getval(schema, 'minimum', Number)
    maxval = getval(schema, 'maximum', Number)
    exclminval = getval(schema, 'exclusiveMinimum', Number)
    exclmaxval = getval(schema, 'exclusiveMaximum', Number)
    multiple_of = getval(schema, 'multipleOf', Number)

    if obj == RETURN_DEFAULT:
        return 0.0

    if not isinstance(obj, Number):
        return ValidationError(schema, name, 'not a number')
    if minval is not None and obj < minval:
        return ValidationError(schema, name, 'less than minimum')
    if maxval is not None and obj > maxval:
        return ValidationError(schema, name, 'greater than maximum')
    if exclminval is not None and obj <= exclminval:
        return ValidationError(schema, name, 'less than or equal to exclusive minimum')
    if exclmaxval is not None and obj >= exclmaxval:
        return ValidationError(schema, name, 'greater than or requal to exclusive maximum')
    if multiple_of is not None and obj % multiple_of != 0:
        return ValidationError(schema, name, 'not a multiple of %d' % multiple_of)
    return obj

def _build_object(obj, schema, **kwargs):
    name = kwargs.get('name')

    properties = getval(schema, 'properties', dict)
    additional_properties = getval(schema, 'additionalProperties', (dict, bool), True)
    required = getval(schema, 'required', list, [])
    property_names = getval(schema, 'propertyNames', dict, {})
    minlen = getval(schema, 'minProperties', int)
    maxlen = getval(schema, 'maxProperties', int)
    dependencies = getval(schema, 'dependencies', dict, {})
    pattern_properties = getval(schema, 'patternProperties', dict, {})

    if obj == RETURN_DEFAULT:
        return {}

    if not isinstance(obj, dict):
        return ValidationError(schema, name, 'not an object')
    if minlen is not None and len(obj) < minlen:
        return ValidationError(schema, name, 'less than minProperties')
    if maxlen is not None and len(obj) > maxlen:
        return ValidationError(schema, name, 'greater than maxProperties')

    for req in required:
        if req not in obj:
            return ValidationError(schema, name, 'missing required property: "%s"' % req)

    for key, dep in dependencies.items():
        if key not in obj:
            continue
        if isinstance(dep, list):
            for val in dep:
                if val not in obj:
                    return ValidationError(schema, name,
                        'missing dependency for "%s": "%s"' % (key, val)
                    )
        elif isinstance(dep, dict):
            result = _build(obj, dep, **kwargs)
            if isinstance(result, Exception):
                return result
        else:
            return ValueError()

    args = kwargs.copy()

    for key, val in obj.items():
        args['name'] = key

        if properties is not None and key in properties:
            result = _build(val, properties[key], **args)
            if isinstance(result, Exception):
                return result
            obj[key] = result
            continue

        if len(pattern_properties) != 0:
            match = False
            for pat, sch in pattern_properties.items():
                if re.search(pat, key):
                    result = _build(val, sch, **args)
                    if isinstance(result, Exception):
                        return result
                    obj[key] = result
                    match = True
                    break
            if match:
                continue

        if isinstance(additional_properties, dict):
            result = _build(val, additional_properties, **args)
            if isinstance(result, Exception):
                return result
            obj[key] = result
        else:
            if additional_properties is False:
                return ValidationError(schema, name, 'cannot have additional properties')
            obj[key] = val

    if properties is not None:
        for key, val in properties.items():
            if key not in obj:
                args['name'] = key
                obj[key] = _build(val.get('default', RETURN_DEFAULT), val, **args)

    if 'pattern' in property_names:
        for key in obj:
            if not re.search(property_names['pattern'], key):
                return ValidationError(schema, name, 'does not match propertyNames pattern')

    return obj

def _build_string(obj, schema, **kwargs):
    name = kwargs.get('name')

    minlen = getval(schema, 'minLength', int)
    maxlen = getval(schema, 'maxLength', int)
    regex = getval(schema, 'pattern', str)
    format_type = getval(schema, 'format', str)

    if obj == RETURN_DEFAULT:
        return ''

    if format_type is not None:
        raise ValueError('not yet implemented')

    if not isinstance(obj, str):
        return ValidationError(schema, name, 'not a string')
    if minlen is not None and len(obj) < minlen:
        return ValidationError(schema, name, 'shorter than minLength')
    if maxlen is not None and len(obj) > maxlen:
        return ValidationError(schema, name, 'longer than maxLength')
    if regex is not None and not re.search(regex, obj):
        return ValidationError(schema, name, 'does not match pattern')
    return obj

def _build_string_array(obj, schema, **kwargs):
    if isinstance(obj, list):
        return _build_string(''.join(obj), schema, **kwargs)
    return _build_string(obj, schema, **kwargs)

_buildtbl = {
    'arr': _build_array,
    'array': _build_array,
    'list': _build_array,
    'bool': _build_boolean,
    'boolean': _build_boolean,
    'const': _build_const,
    'enum': _build_enum,
    'int': _build_integer,
    'integer': _build_integer,
    'null': _build_null,
    'none': _build_null,
    'num': _build_number,
    'number': _build_number,
    'float': _build_number,
    'obj': _build_object,
    'object': _build_object,
    'dict': _build_object,
    'str': _build_string,
    'string': _build_string,
    'str_arr': _build_string_array,
    'string_array': _build_string_array,
}
