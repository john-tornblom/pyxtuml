# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import unittest
import os

import xtuml.io

class TestModel(unittest.TestCase):

    def setUp(self):
        base_dir = '%s/../resources' % os.path.dirname(__file__)
        loader = xtuml.io.load.ModelLoader()
        loader.build_parser()
        loader.filename_input('%s/ooaofooa_schema.sql' % base_dir)
        loader.filename_input('%s/Globals.xtuml' % base_dir)
        self.metamodel = loader.build_metamodel()

    def tearDown(self):
        del self.metamodel

    def testSelectAny(self):
        m = self.metamodel
        self.assertNotEqual(m.select_any('S_DT'), None)

    def testSelectOne(self):
        m = self.metamodel
        self.assertNotEqual(m.select_one('S_DT'), None)
        
    def testSelectAnyWhere(self):
        m = self.metamodel
        inst = m.select_any('S_DT', lambda inst: inst.Name == 'void')
        self.assertEqual(inst.Name, 'void')
        
    def testNavOne(self):
        m = self.metamodel
        s_dt = m.select_any('S_DT', lambda inst: inst.name == 'void')
        pe_pe = m.navigate_one(s_dt).PE_PE[8001](lambda inst: True)
        self.assertEqual(s_dt.DT_ID, pe_pe.Element_ID)
        
    def testNavMany(self):
        m = self.metamodel
        s_dt = m.select_many('S_DT')
        pe_pe = m.navigate_many(s_dt).PE_PE[8001](lambda inst: True)
        self.assertEqual(len(s_dt), len(pe_pe))


def populate_suite(s):
    loader = unittest.TestLoader()
    s.addTests(loader.loadTestsFromTestCase(TestModel))
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()