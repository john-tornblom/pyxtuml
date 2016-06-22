# encoding: utf-8
# Copyright (C) 2015-2016 John Törnblom
'''
Check a bridgepoint model for association constraint violations in its 
metamodel (ooaofooa).
'''

import logging
import optparse
import sys
import xtuml
from bridgepoint import ooaofooa


logger = logging.getLogger('consistency_check')


def main():
    parser = optparse.OptionParser(usage="%prog [options] <model_path> [another_model_path...]",
                                   version=xtuml.version.complete_string,
                                   formatter=optparse.TitledHelpFormatter())
    
    parser.set_description(__doc__.strip())
    
    parser.add_option("-r", "-R", dest="rel_ids", type='int', metavar="<number>",
                      help="limit consistency check to one or more associations",
                      action="append", default=[])

    parser.add_option("-k", dest="kinds", type='string', metavar="<key letter>",
                      help="limit check for uniqueness constraint violations to one or more classes",
                      action="append", default=[])
    
    parser.add_option("-g", "--globals", dest="globals",
                      help="add builtin global data types automatically, e.g. boolean, integer and real",
                      action="store_true", default=False)
                      
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
    
    loader = ooaofooa.Loader(load_globals=opts.globals)
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

