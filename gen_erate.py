#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import optparse
import logging
import sys

from xtuml import model
from xtuml import io
from xtuml import rsl
from xtuml import version


current_id = 0
def next_id():
    global current_id
    current_id += 1
    return current_id
    
    
def main():
    parser = optparse.OptionParser(usage="%prog [OPTION]... {filename}", version=version.complete_string, formatter=optparse.TitledHelpFormatter())
    parser.add_option("-i", "--import", dest="imports", metavar="PATH", help="import model information from PATH", action="append", default=[])
    parser.add_option("-e", "--emit", dest='emit', metavar="WHEN", choices=['never', 'change', 'always'], action="store", help="choose when to emit (never, change, always)", default='change')
    parser.add_option("-f", "--force", dest='force', action="store_true", help="make read-only emit files writable", default=False)
    parser.add_option("-d", "--diff", dest='diff', metavar="PATH", action="store", help="save a diff of all emits to PATH", default=None)
    parser.add_option("-v", "--verbosity", dest='verbosity', action="count", help="increase debug logging level", default=1)
    
    
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
    
    loader = io.load.ModelLoader()
    loader.build_parser()

    for filename in opts.imports:
        loader.filename_input(filename)

    id_generator = model.IdGenerator(next_id)
    metamodel = loader.build_metamodel(id_generator)
    
    if opts.diff:
        with open(opts.diff, 'w') as f:
            f.write(' '.join(sys.argv))
            f.write('\n')
            
    rt = rsl.runtime.Runtime(metamodel, opts.emit, opts.force, opts.diff)
    for filename in args:
        ast = rsl.parse_file(filename)
        rsl.evaluate(rt, ast)
    
if __name__ == '__main__':
    main()
