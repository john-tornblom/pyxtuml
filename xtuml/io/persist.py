# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import uuid


def serialize_model(model):
    s = ''
    for lst in model.instances.values():
        for inst in lst:
            table = inst.__class__.__name__
            params = model.param_names[table]
            types = model.param_types[table]
            s += serialize_instance(inst, table, zip(params, types))
            
    return s


def serialize_instance(inst, table, attributes):
    attr_count = 0
        
    s = 'INSERT INTO %s VALUES (' % table
    for name, ty in attributes:
        value = getattr(inst, name)
        s += '\n    '
        if   isinstance(value, bool):
            s += '%d' % int(value)

        elif isinstance(value, str):
            s += "'%s'" % value.replace("'", "''")

        elif isinstance(value, int):
            s += '%d' % value

        elif isinstance(value, long):
            s += '%f' % value

        elif isinstance(value, uuid.UUID):
            s += '"%s"' % value

        attr_count += 1
        if attr_count < len(attributes):
            s += ', -- %s : %s' % (name, ty)
        else:
            s += ' -- %s : %s' % (name, ty)

    s += '\n);\n'

    return s
