# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import unittest

from . import rsl
from . import io

def run():
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    runner.run(rsl.suite())
    runner.run(io.suite())
