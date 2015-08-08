#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom
import logging
import unittest
import sys

try:
    from setuptools import setup
    from setuptools import Command
    from setuptools.command.build_py import build_py
except ImportError:
    from distutils.core import setup
    from distutils.core  import Command
    from distutils.command.build_py import build_py

import xtuml


logging.basicConfig(level=logging.DEBUG)


class BuildCommand(build_py):
    
    def run(self):
        xtuml.load_metamodel([])
        build_py.run(self)


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
      description='Library for parsing, manipulating, and generating BridgePoint xtUML models',
      author='John Törnblom',
      author_email='john.tornblom@gmail.com',
      url='https://github.com/john-tornblom/pyxtuml',
      license='GPLv3',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Code Generators',
          'Topic :: Software Development :: Compilers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4'],
      keywords='xtuml bridgepoint',
      platforms=["Linux"],
      packages=['xtuml', 'bridgepoint'],
      requires=['ply'],
      cmdclass={'build_py': BuildCommand,
                'test': TestCommand}
      )

