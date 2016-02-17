# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Check an xtuml model for association constraint violations in its metamodel.
'''

import logging
import optparse
import sys
import xtuml


logger = logging.getLogger('consistency_check')


def pretty_to_link(inst, from_link, to_link):
    '''
    Create a human-readable representation of a link on the 'TO'-side
    '''
    values = ''
    prefix = ''
 
    for name, ty in inst.__a__:
        if name in from_link.ids:
            value = getattr(inst, name)
            value = xtuml.serialize_value(value, ty)
            idx = from_link.ids.index(name)
            name = to_link.ids[idx]
            values += '%s%s=%s' % (prefix, name, value)
            prefix = ', '
                
    return '%s(%s)' % (to_link.kind, values)
        

def pretty_from_link(inst, from_link, to_link):
    '''
    Create a human-readable representation of a link on the 'FROM'-side
    '''
    values = ''
    prefix = ''
 
    for name, ty in inst.__a__:
        if name in inst.__i__:
            value = getattr(inst, name)
            value = xtuml.serialize_value(value, ty)
            values += '%s%s=%s' % (prefix, name, value)
            prefix = ', '
                
    return '%s(%s)' % (from_link.kind, values)


def pretty_unique_identifier(inst, identifier):
    '''
    Create a human-readable representation a unique identifier.
    '''
    values = ''
    prefix = ''
    
    for name, ty in inst.__a__:
        if name in inst.__u__[identifier]:
            value = getattr(inst, name)
            value = xtuml.serialize_value(value, ty)
            values += '%s%s=%s' % (prefix, name, value)
            prefix = ', '
                    
    return '%s(%s)' % (identifier, values)

def check_uniqueness_constraint(m, kind=None):
    '''
    Check the model for uniqueness constraint violations.
    '''
    if kind is None:
        classes = m.classes.values()
    else:
        classes = [m.classes[kind.upper()]]
    
    res = True
    for Cls in classes:
        for inst in m.select_many(Cls.__name__):
            for identifier in Cls.__u__.keys():
                kwargs = dict()
                for name in Cls.__u__[identifier]:
                    kwargs[name] = getattr(inst, name)
                
                where_clause = xtuml.where_eq(**kwargs)
                s = m.select_many(Cls.__name__, where_clause)
                if len(s) != 1:
                    res = False
                    id_string = pretty_unique_identifier(inst, identifier)
                    logger.warning('uniqueness constraint violation in %s, %s' 
                                   % (Cls.__name__, id_string))

    return res


def check_link_integrity(m, rel_id, from_link, to_link):
    '''
    Check the model for integrity violations on an association in a particular direction.
    '''
    res = True
    for inst in m.select_many(from_link.kind):
        nav_chain = xtuml.navigate_many(inst)
        q_set = nav_chain.nav(to_link.kind, rel_id, to_link.phrase)()

        if(len(q_set) < 1 and not to_link.is_conditional) or (
          (len(q_set) > 1 and not to_link.is_many)):
            res = False
            logger.warning('integrity violation in '
                           '%s --(%s)--> %s' % (pretty_from_link(inst, from_link, to_link),
                                                rel_id,
                                                pretty_to_link(inst, from_link, to_link)))
    
    return res


def check_association_integrity(m, rel_id=None):
    '''
    Check the model for integrity violations on association(s).
    '''
    if isinstance(rel_id, int):
        rel_id = 'R%d' % rel_id
            
    res = True
    for ass in m.associations:
        if rel_id in [ass.id, None]:
            res &= check_link_integrity(m, ass.id, ass.source, ass.target)
            res &= check_link_integrity(m, ass.id, ass.target, ass.source)

    return res


def main():
    parser = optparse.OptionParser(usage="%prog [options] <sql_file> [another_sql_file...].",
                                   version=xtuml.version.complete_string,
                                   formatter=optparse.TitledHelpFormatter())
    
    parser.set_description(__doc__.strip())
    
    parser.add_option("-r", "-R", dest="rel_ids", type='int', metavar="<number>",
                      help="limit consistency check to one or more associations",
                      action="append", default=[])

    parser.add_option("-k", dest="kinds", type='string', metavar="<key letter>",
                      help="limit check for uniqueness constraint violations to one or more classes",
                      action="append", default=[])
    
    parser.add_option("-v", "--verbosity", dest='verbosity', action="count",
                      help="increase debug logging level", default=1)
    
    (opts, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(1)
        
    levels = {
              0: logging.ERROR,
              1: logging.WARNING,
              2: logging.INFO,
              3: logging.DEBUG,
    }
    logging.basicConfig(level=levels.get(opts.verbosity, logging.DEBUG))
    
    loader = xtuml.ModelLoader()
    for filename in args:
        loader.filename_input(filename)

    m = loader.build_metamodel()
    
    error = False
    for rel_id in opts.rel_ids:
        error |= xtuml.check_association_integrity(m, rel_id)
    
    if not opts.rel_ids:
        error |= xtuml.check_association_integrity(m)

    for kind in opts.kinds:
        error |= xtuml.check_uniqueness_constraint(m, kind)
    
    if not opts.kinds:
        error |= xtuml.check_uniqueness_constraint(m)
        
    sys.exit(error)
    
    
if __name__ == '__main__':
    main()

