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


def populate_suite(s):
    loader = unittest.TestLoader()
    s.addTests(loader.loadTestsFromModule(binop))
    s.addTests(loader.loadTestsFromModule(emit))
    s.addTests(loader.loadTestsFromModule(loop))
    s.addTests(loader.loadTestsFromModule(select))
    s.addTests(loader.loadTestsFromModule(invoke))
    s.addTests(loader.loadTestsFromModule(ifs))
    s.addTests(loader.loadTestsFromModule(prints))
    s.addTests(loader.loadTestsFromModule(const))
    s.addTests(loader.loadTestsFromModule(info))
    s.addTests(loader.loadTestsFromModule(parsekw))
    s.addTests(loader.loadTestsFromModule(intrinsic))
    s.addTests(loader.loadTestsFromModule(variable))
    s.addTests(loader.loadTestsFromModule(format))
    s.addTests(loader.loadTestsFromModule(typesys))
    s.addTests(loader.loadTestsFromModule(symtab))
