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
    w = eval.EvalWalker(rt)
    #w.visitors.append(xtuml.tools.NodePrintVisitor())
    w.accept(ast)

    
if __name__ == "__main__":
    parse_file(sys.argv[1])
