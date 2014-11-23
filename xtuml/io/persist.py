# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import uuid
import logging


logger = logging.getLogger(__name__)


def serialize_model(model):
    s = ''
    for lst in model.instances.values():
        for inst in lst:
            table = inst.__class__.__name__
            params = model.param_names[table]
            types = model.param_types[table]
            s += serialize_instance(inst, table, zip(params, types))
            
    return s


def default_value(ty):
    if   ty == 'boolean'  : return False
    elif ty == 'integer'  : return 0
    elif ty == 'real'     : return 0.0
    elif ty == 'unique_id': return uuid.UUID(int=0)
    elif ty == 'string'   : return ''
    else                  : return None


def serialize_value(value):
    if   isinstance(value, bool):
        return '%d' % int(value)

    elif isinstance(value, str):
        return "'%s'" % value.replace("'", "''")

    elif isinstance(value, int):
        return '%d' % value

    elif isinstance(value, long):
        return '%f' % value

    elif isinstance(value, uuid.UUID):
        return '"%s"' % value

    else:
        return None


def serialize_instance(inst, table, attributes):
    attr_count = 0
        
    s = 'INSERT INTO %s VALUES (' % table
    for name, ty in attributes:
        value = getattr(inst, name)
        s += '\n    '

        s_val = serialize_value(value)
        if s_val is None:
            msg = 'type error while serializing "%s.%s = %s"' % (table, name, repr(value))
            value = default_value(ty)
            logger.warning('%s, using the default %s value %s' % (msg, ty, repr(value)))
            s_val = serialize_value(value)
 
        s += s_val

        attr_count += 1
        if attr_count < len(attributes):
            s += ', -- %s : %s' % (name, ty)
        else:
            s += ' -- %s : %s' % (name, ty)

    s += '\n);\n'

    return s
