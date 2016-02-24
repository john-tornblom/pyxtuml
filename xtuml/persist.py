# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Serialize xtuml models and its schema to an sql-based file format and persist
to disk.
'''

import uuid
import logging

import xtuml


logger = logging.getLogger(__name__)


def serialize_value(value, ty):
    '''
    Serialize a value from an xtuml metamodel instance.
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
    
    
def serialize_instance(instance):
    '''
    Serialize an *instance* from a metamodel.
    '''
    attr_count = 0

    table = instance.__class__.__name__
    s = 'INSERT INTO %s VALUES (' % table
    for name, ty in instance.__a__:
        value = getattr(instance, name)
            
        s += '\n    '
        s += serialize_value(value, ty)

        attr_count += 1
        if attr_count < len(instance.__a__):
            s += ', -- %s : %s' % (name, ty)
        else:
            s += ' -- %s : %s' % (name, ty)

    s += '\n);\n'

    return s


def serialize_instances(metamodel):
    '''
    Serialize all instances in a *metamodel*.
    '''
    s = ''
    for lst in metamodel.instances.values():
        for inst in lst:
            s += serialize_instance(inst)
    
    return s


def serialize_association_link(lnk):
    '''
    Serialize an xtuml metamodel association link.
    '''
    s = '%s %s (%s)' % (lnk.cardinality.upper(),
                        lnk.kind,
                        ', '.join(lnk.ids))
    
    if lnk.phrase:
        s += " PHRASE '%s'" % lnk.phrase
        
    return s


def serialize_association(ass):
    '''
    Serialize an xtuml metamodel association.
    '''
    source = serialize_association_link(ass.source)
    target = serialize_association_link(ass.target)
    return 'CREATE ROP REF_ID %s FROM %s TO %s;\n' % (ass.id,
                                                      source,
                                                      target)


def serialize_class(Cls):
    '''
    Serialize an xtUML metamodel class.
    '''
    s = 'CREATE TABLE %s (\n    ' % Cls.__name__
    s += ',\n    '.join(['%s %s' % (name, ty.upper()) for name, ty in Cls.__a__])
    s += '\n);\n'

    return s

def serialize_unique_identifiers(metamodel):
    s = ''
    
    for Cls in sorted(metamodel.classes.values()):
        for name, attributes in Cls.__u__.items():
            attributes = ', '.join(attributes)
            s += 'CREATE UNIQUE INDEX %s ON %s (%s);\n' % (name,
                                                           Cls.__name__,
                                                           attributes)

    return s

def serialize_schema(metamodel):
    '''
    Serialize all class and association definitions in a *metamodel*.
    '''
    s = ''
    for kind in sorted(metamodel.classes.keys()):
        s += serialize_class(metamodel.classes[kind])
    
    for ass in sorted(metamodel.associations, key=lambda x: x.id):
        s += serialize_association(ass)
    
    return s


def serialize_database(metamodel):
    '''
    Serialize all instances, class definitions, association definitions, and
    unique identifiers  in a *metamodel*.
    '''
    schema = serialize_schema(metamodel)
    instances = serialize_instances(metamodel)
    identifiers = serialize_unique_identifiers(metamodel)
    
    return ''.join([schema, instances, identifiers])


def serialize(resource):
    '''
    Serialize some xtuml *resource*, e.g. an instance or a complete metamodel.
    '''
    if isinstance(resource, xtuml.MetaModel):
        return serialize_database(resource)

    elif isinstance(resource, type) and issubclass(resource, xtuml.BaseObject):
        return serialize_class(resource)
    
    elif isinstance(resource, xtuml.Association):
        return serialize_association(resource)

    elif isinstance(resource, xtuml.AssociationLink):
        return serialize_association_link(resource)
    
    elif isinstance(resource, xtuml.BaseObject):
        return serialize_instance(resource)


def persist_instances(metamodel, path):
    '''
    Persist all instances in a *metamodel* by serializing them and saving to a 
    *path* on disk.
    '''
    with open(path, 'w') as f:
        for lst in metamodel.instances.values():
            for inst in lst:
                s = serialize_instance(inst)
                f.write(s)


def persist_schema(metamodel, path):
    '''
    Persist all class and association definitions in a *metamodel* by 
    serializing them and saving to a *path* on disk.
    '''
    with open(path, 'w') as f:
        for kind in sorted(metamodel.classes.keys()):
            s = serialize_class(metamodel.classes[kind])
            f.write(s)
            
        for ass in sorted(metamodel.associations, key=lambda x: x.id):
            s = serialize_association(ass)
            f.write(s)


def persist_unique_identifiers(metamodel, path):
    '''
    Persist all unique identifiers in a *metamodel* by serializing them and
    saving to a *path* on disk.
    '''
    with open(path, 'w') as f:
        for Cls in sorted(metamodel.classes.values()):
            for name, attributes in Cls.__u__.items():
                attributes = ', '.join(attributes)
                s = 'CREATE UNIQUE INDEX %s ON %s (%s);\n' % (name,
                                                              Cls.__name__,
                                                              attributes)
                f.write(s)


def persist_database(metamodel, path):
    '''
    Persist all instances, class definitions and association definitions in a
    *metamodel* by serializing them and saving to a *path* on disk.
    '''
    with open(path, 'w') as f:
        for kind in sorted(metamodel.classes.keys()):
            Cls = metamodel.classes[kind]
            s = serialize_class(Cls)
            f.write(s)
            
            for name, attributes in Cls.__u__.items():
                attributes = ', '.join(attributes)
                s = 'CREATE UNIQUE INDEX %s ON %s (%s);\n' % (name,
                                                              Cls.__name__,
                                                              attributes)
                f.write(s)
                
        for ass in sorted(metamodel.associations, key=lambda x: x.id):
            s = serialize_association(ass)
            f.write(s)

        for lst in metamodel.instances.values():
            for inst in lst:
                s = serialize_instance(inst)
                f.write(s)
