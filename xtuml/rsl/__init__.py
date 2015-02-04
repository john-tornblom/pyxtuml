# encoding: utf-8
# Copyright (C) 2014 John Törnblom
'''
Parsing and evaluation of the rule-specification language (RSL).  
'''


import os
import sys
import logging

from . import parse
from . import eval
from . import pyrepr
from . import runtime

import xtuml.tools


logger = logging.getLogger(__name__)


def parse_file(filename):
    parser = parse.RSLParser()
    return parser.filename_input(filename)


def parse_text(text, filename=''):
    parser = parse.RSLParser()
    return parser.text_input(text, filename)


def evaluate(rt, ast):
    # Unfortunately, the PyRepr translator is not working right now.
    # It will probably require a major rewrite in order to get the 
    # scope rules correct when including files.
    if True:
        w = eval.EvalWalker(rt)
        #w.visitors.append(xtuml.tools.NodePrintVisitor())
        w.accept(ast)
    else:
        w = pyrepr.PyReprWalker(rt)
        #w.visitors.append(xtuml.tools.NodePrintVisitor())
        py_code = w.accept(ast)
        logger.debug('%s\n' % py_code)

        ast = compile(py_code, ast.filename, 'exec')
        try:
            exec(ast, {'_rt': rt})
        except Exception as e:
            sys.exit(e)
    
if __name__ == "__main__":
    parse_file(sys.argv[1])
