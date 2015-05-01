# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Serialize xtuml models to an sql-based file format and persist to disk.
'''


import uuid
import logging


logger = logging.getLogger(__name__)


def serialize_value(value):
    if   isinstance(value, bool):
        return '%d' % int(value)

    elif isinstance(value, str):
        return "'%s'" % value.replace("'", "''")

    elif isinstance(value, int):
        return '%d' % value
    
    elif isinstance(value, float):
        return '%f' % value

    elif isinstance(value, uuid.UUID):
        return '"%s"' % value


def serialize_instance(inst, table, attributes):
    attr_count = 0
    attributes = list(attributes)

    s = 'INSERT INTO %s VALUES (' % table
    for name, ty in attributes:
        value = getattr(inst, name)
        s += '\n    '
        s += serialize_value(value)

        attr_count += 1
        if attr_count < len(attributes):
            s += ', -- %s : %s' % (name, ty)
        else:
            s += ' -- %s : %s' % (name, ty)

    s += '\n);\n'

    return s


def serialize_metamodel(metamodel):
    s = ''
    for lst in metamodel.instances.values():
        for inst in lst:
            table = inst.__class__.__name__
            params = metamodel.param_names[table]
            types = metamodel.param_types[table]
            s += serialize_instance(inst, table, zip(params, types))
            
    return s


def persist_metamodel(metamodel, path):
    with open(path, 'w') as f:
        s = serialize_metamodel(metamodel)
        f.write(s)

