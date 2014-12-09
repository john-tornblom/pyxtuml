#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import os
from distutils.core import setup
from distutils.core import Command


class PrepareCommand(Command):
    description = "Prepare the source code by generating lexers and parsers"
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        os.system('runantlr -o xtuml/oal xtuml/oal/parser.g')
        os.system('runantlr -o xtuml/oal xtuml/oal/lexer.g')

        os.system('runantlr -o xtuml/sql xtuml/sql/parser.g')
        os.system('runantlr -o xtuml/sql xtuml/sql/lexer.g')


long_desc = "pyxtuml is a python library for parsing, manipulating, and generating BridgePoint xtUML models."

setup(name='pyxtuml',
      version='0.0.1',
      description='pyxtuml',
      long_description=long_desc,
      author='John Törnblom',
      author_email='john.tornblom@gmail.com',
      url='https://github.com/john-tornblom/pyxtuml',
      license='GPLv3',
      platforms=["Linux"],
      packages=['xtuml', 'xtuml.io', 'xtuml.oal'],
      requires=['ply', 'antlr'],
      cmdclass={'prepare': PrepareCommand},
      )

