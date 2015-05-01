#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom
import logging
import unittest
import sys

from distutils.core import setup
from distutils.core import Command

import xtuml


logging.basicConfig(level=logging.DEBUG)


class PrepareCommand(Command):
    description = "Prepare the source code by generating lexers and parsers"
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        xtuml.load_metamodel([])


class TestCommand(Command):
    description = "Execute unit tests"
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        suite = unittest.TestLoader().discover('tests')
        runner = unittest.TextTestRunner(verbosity=2, buffer=True)
        exit_code = not runner.run(suite).wasSuccessful()
        sys.exit(exit_code)


setup(name='pyxtuml',
      version=xtuml.version.release,
      description='pyxtuml',
      long_description="pyxtuml is a python library for parsing, manipulating, and generating BridgePoint xtUML models.",
      author='John Törnblom',
      author_email='john.tornblom@gmail.com',
      url='https://github.com/john-tornblom/pyxtuml',
      license='GPLv3',
      platforms=["Linux"],
      packages=['xtuml'],
      requires=['ply'],
      cmdclass={'prepare': PrepareCommand, 'test': TestCommand}
      )

