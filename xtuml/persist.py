# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Serialize xtuml models and its schema to an sql-based file format and persist to disk.
'''


import uuid
import logging


logger = logging.getLogger(__name__)


def serialize_value(value, ty):
    '''
    Serialize a value from a xtUML meta model instance.
    '''
    ty = ty.upper()
    
    null_value = {
        'BOOLEAN'   : False,
        'INTEGER'   : 0,
        'REAL'      : 0.0,
        'STRING'    : '',
        'UNIQUE_ID' : 0
    }
    
    transfer_fn = {
        'BOOLEAN'     : lambda v: '%d' % int(v),
        'INTEGER'     : lambda v: '%d' % v,
        'REAL'        : lambda v: '%f' % v,
        'STRING'      : lambda v: "'%s'" % v.replace("'", "''"),
        'UNIQUE_ID'   : lambda v: '"%s"' % uuid.UUID(int=v)
    }

    if value is None:
        value = null_value[ty]
    
    return transfer_fn[ty](value)
    
    
def serialize_instance(inst):
    '''
    Serialize an xtUML meta model instance.
    '''
    attr_count = 0

    
    
    table = inst.__class__.__name__
    s = 'INSERT INTO %s VALUES (' % table
    for name, ty in inst.__a__:
        value = getattr(inst, name)
            
        s += '\n    '
        s += serialize_value(value, ty)

        attr_count += 1
        if attr_count < len(inst.__a__):
            s += ', -- %s : %s' % (name, ty)
        else:
            s += ' -- %s : %s' % (name, ty)

    s += '\n);\n'

    return s


def serialize_instances(metamodel):
    '''
    Serialize instances located in a xtUML meta model.
    '''
    s = ''
    for lst in metamodel.instances.values():
        for inst in lst:
            s += serialize_instance(inst)
    
    return s


def serialize_association_link(lnk):
    '''
    Serialize an xtUML meta model association link.
    '''
    s = '%s %s (%s)' % (lnk.cardinality.upper(),
                        lnk.kind,
                        ', '.join(lnk.ids))
    
    if lnk.phrase:
        s += " PHRASE '%s'" % lnk.phrase
        
    return s


def serialize_association(ass):
    '''
    Serialize an xtUML meta model association.
    '''
    source = serialize_association_link(ass.source)
    target = serialize_association_link(ass.target)
    return 'CREATE ROP REF_ID %s FROM %s TO %s;\n' % (ass.id,
                                                      source,
                                                      target)


def serialize_class(Cls):
    '''
    Serialize an xtUML meta model class.
    '''
    s = 'CREATE TABLE %s (\n    ' % Cls.__name__
    s += ',\n    '.join(['%s %s' % (name, ty.upper()) for name, ty in Cls.__a__])
    s += '\n);\n'

    return s


def serialize_schema(metamodel):
    '''
    Serialize schema for a xtUML meta model.
    '''
    s = ''
    for kind in sorted(metamodel.classes.keys()):
        s += serialize_class(metamodel.classes[kind])
    
    for ass in sorted(metamodel.associations, key=lambda x: x.id):
        s += serialize_association(ass)
    
    return s


def persist_instances(metamodel, path):
    '''
    Persist instances from a meta model to disk.
    '''
    with open(path, 'w') as f:
        s = serialize_instances(metamodel)
        f.write(s)


def persist_schema(metamodel, path):
    '''
    Persist a schema of a meta model to disk.
    '''
    with open(path, 'w') as f:
        s = serialize_schema(metamodel)
        f.write(s)

