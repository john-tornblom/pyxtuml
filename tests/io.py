# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import unittest
import os

from xtuml import model
from xtuml import io


class TestLoader(unittest.TestCase):

    def setUp(self):
        self.loader = io.load.ModelLoader()
        self.loader.build_parser()

    def tearDown(self):
        del self.loader

    def testLoadGlobals(self):
        base_dir = '%s/../resources' % os.path.dirname(__file__)
        self.loader.filename_input('%s/ooaofooa_schema.sql' % base_dir)
        self.loader.filename_input('%s/Globals.xtuml' % base_dir)

        id_generator = model.IdGenerator()
        metamodel = self.loader.build_metamodel(id_generator)
        self.assertTrue(metamodel.select_any('S_DT', Name='integer') is not None)
        
def suite():
    loader = unittest.TestLoader()
    s = loader.loadTestsFromTestCase(TestLoader)
    
    return s

