#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import os
import logging

from distutils.core import setup
from distutils.core import Command

import xtuml.io.load
import xtuml.rsl.parse
import xtuml.version

logging.basicConfig(level=logging.DEBUG)

class PrepareCommand(Command):
    description = "Prepare the source code by generating lexers and parsers"
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        loader = xtuml.io.load.ModelLoader()
        loader.build_parser()
        
        xtuml.rsl.parse.RSLParser()
        
        #os.system('runantlr -o xtuml/oal xtuml/oal/parser.g')
        #os.system('runantlr -o xtuml/oal xtuml/oal/lexer.g')


class TestCommand(Command):
    description = "Execute unit tests"
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        import tests
        import sys
        sys.exit(tests.run())


long_desc = "pyxtuml is a python library for parsing, manipulating, and generating BridgePoint xtUML models."

setup(name='pyxtuml',
      version=xtuml.version.release,
      description='pyxtuml',
      long_description=long_desc,
      author='John Törnblom',
      author_email='john.tornblom@gmail.com',
      url='https://github.com/john-tornblom/pyxtuml',
      license='GPLv3',
      platforms=["Linux"],
      packages=['xtuml', 'xtuml.io', 'xtuml.rsl'],
      requires=['ply'],
      cmdclass={'prepare': PrepareCommand, 'test': TestCommand},
      scripts=['gen_erate.py']
      )

