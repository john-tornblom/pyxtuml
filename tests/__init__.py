# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import unittest

from . import rsl
from . import io

def run():
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    rc = runner.run(rsl.suite()).wasSuccessful()
    rc &= runner.run(io.suite()).wasSuccessful()
    
    return not rc
