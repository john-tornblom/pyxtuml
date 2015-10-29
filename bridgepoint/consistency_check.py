# encoding: utf-8
# Copyright (C) 2015 John Törnblom
import logging
import optparse
import sys
import xtuml
from bridgepoint import ooaofooa


logger = logging.getLogger('consistency_check')


def main():
    parser = optparse.OptionParser(usage="bridgepoint.consistency_check [options] file_or_path file_or_path ...", 
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
    
    loader = ooaofooa.Loader()
    for filename in args:
        loader.filename_input(filename)

    m = loader.build_metamodel(ignore_undefined_classes=True)
    
    error = False
    for rel_id in opts.r:
        error |= xtuml.check_association_integrity(m, rel_id)
    
    if not opts.r:
        error |= xtuml.check_association_integrity(m)

    sys.exit(error)
    
    
if __name__ == '__main__':
    main()


    