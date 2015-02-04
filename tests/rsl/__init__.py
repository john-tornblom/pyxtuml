# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import unittest

from . import binop
from . import const
from . import emit
from . import format
from . import ifs
from . import info
from . import intrinsic
from . import invoke
from . import loop
from . import parsekw
from . import prints
from . import select
from . import symtab
from . import typesys
from . import variable


def run():
    loader = unittest.TestLoader()

    suite = loader.loadTestsFromModule(binop)
    suite.addTests(loader.loadTestsFromModule(emit))
    suite.addTests(loader.loadTestsFromModule(loop))
    suite.addTests(loader.loadTestsFromModule(select))
    suite.addTests(loader.loadTestsFromModule(invoke))
    suite.addTests(loader.loadTestsFromModule(ifs))
    suite.addTests(loader.loadTestsFromModule(prints))
    suite.addTests(loader.loadTestsFromModule(const))
    suite.addTests(loader.loadTestsFromModule(info))
    suite.addTests(loader.loadTestsFromModule(parsekw))
    suite.addTests(loader.loadTestsFromModule(intrinsic))
    suite.addTests(loader.loadTestsFromModule(variable))
    suite.addTests(loader.loadTestsFromModule(format))
    suite.addTests(loader.loadTestsFromModule(typesys))
    
    suite.addTests(loader.loadTestsFromModule(symtab))
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    return runner.run(suite)

