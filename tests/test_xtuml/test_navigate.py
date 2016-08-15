# encoding: utf-8
# Copyright (C) 2016 John Törnblom

import unittest
import xtuml
import bridgepoint


class TestNavigation(unittest.TestCase):
    '''
    Test suite for xtuml navigate operations
    '''
    def setUp(self):
        self.m = bridgepoint.load_metamodel()

    def tearDown(self):
        del self.m

    def test_navigate_one(self):
        s_dt = self.m.select_any('S_DT',  xtuml.where_eq(Name='void'))
        pe_pe = xtuml.navigate_one(s_dt).PE_PE[8001](lambda inst: True)
        self.assertEqual(s_dt.DT_ID, pe_pe.Element_ID)
        
    def test_navigate_many(self):
        s_dt = self.m.select_many('S_DT')
        pe_pe = xtuml.navigate_many(s_dt).PE_PE[8001](lambda inst: True)
        self.assertEqual(len(s_dt), len(pe_pe))
   
    def test_navigate_suptype(self):
        s_dt = self.m.select_any('S_DT', xtuml.where_eq(Name='void'))
        s_cdt = xtuml.navigate_subtype(s_dt, 17)
        self.assertTrue(s_cdt)
        self.assertIsInstance(s_cdt, self.m.find_class('S_CDT'))

    def test_navigate_none(self):
        self.assertIsNone(xtuml.navigate_one(None)())
        self.assertIsNone(xtuml.navigate_subtype(None, 0))
        self.assertEqual(len(xtuml.navigate_many(None)()), 0)

    def test_navigate_invalid_handle(self):
        self.assertRaises(xtuml.MetaException, xtuml.navigate_one, 50)

        
if __name__ == "__main__":
    unittest.main()

