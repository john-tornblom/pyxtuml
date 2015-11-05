# encoding: utf-8
# Copyright (C) 2015 John Törnblom
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
            prefix=', '
                
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
            prefix=', '
                
    return '%s(%s)' % (from_link.kind, values)


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
    parser = optparse.OptionParser(usage="xtuml.consistency_check [options] file.sql file2.sql ...", 
                                   version=xtuml.version.complete_string, 
                                   formatter=optparse.TitledHelpFormatter())
    
    parser.add_option("-r", dest="r", type='int', metavar="<number>", 
                      help="limit consistency check to one or more associations", 
                      action="append", default=[])

    (opts, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(1)
        
    logging.basicConfig(level=logging.WARNING)
    
    loader = xtuml.ModelLoader()
    for filename in args:
        loader.filename_input(filename)

    m = loader.build_metamodel()
    
    error = False
    for rel_id in opts.r:
        error |= xtuml.check_association_integrity(m, rel_id)
    
    if not opts.r:
        error |= xtuml.check_association_integrity(m)

    sys.exit(error)
    
    
if __name__ == '__main__':
    main()


    