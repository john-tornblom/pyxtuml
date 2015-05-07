# encoding: utf-8
# Copyright (C) 2014-2015 John Törnblom

import unittest
import os

import xtuml

class TestModel(unittest.TestCase):
    resources = os.path.dirname(__file__) + os.sep + '..' + os.sep + 'resources'
    schema = resources + os.sep + 'ooaofooa_schema.sql'
    globals = resources + os.sep + 'Globals.xtuml'
    
    def setUp(self):
        self.metamodel = xtuml.load_metamodel([self.schema, self.globals])

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
        pe_pe = xtuml.navigate_one(s_dt).PE_PE[8001](lambda inst: True)
        self.assertEqual(s_dt.DT_ID, pe_pe.Element_ID)
        
    def testNavMany(self):
        m = self.metamodel
        s_dt = m.select_many('S_DT')
        pe_pe = xtuml.navigate_many(s_dt).PE_PE[8001](lambda inst: True)
        self.assertEqual(len(s_dt), len(pe_pe))
   

if __name__ == "__main__":
    unittest.main()

