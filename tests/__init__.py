# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import unittest

from . import rsl
from . import io
from . import model

def run():
    suite = unittest.TestSuite()
    rsl.populate_suite(suite)
    io.populate_suite(suite)
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    return not runner.run(suite).wasSuccessful()
