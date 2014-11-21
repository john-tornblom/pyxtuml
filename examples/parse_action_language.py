#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import sys
import os

base_dir = '%s/../' % os.path.dirname(__file__)
sys.path.append(base_dir)

from xtuml import oal
from xtuml import tools

action_code = '''
    x = "Hello world!";
    LOG::LogInfo(message: x);
    return True;
'''

ast = oal.parse(action_code)

walker = tools.Walker()
walker.visitors.append(tools.NodePrintVisitor())
walker.accept(ast)
