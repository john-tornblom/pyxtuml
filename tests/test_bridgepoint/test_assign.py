# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from tests.test_bridgepoint.utils import PrebuildFunctionTestCase
from tests.test_bridgepoint.utils import prebuild_docstring

from xtuml import navigate_one as one


class TestAssign(PrebuildFunctionTestCase):

    @prebuild_docstring
    def test_positive_integer(self):
        '''assign x = 1;'''
        act_ai = self.metamodel.select_one('ACT_AI')
        self.assertIsNotNone(act_ai)
        
        act_smt = one(act_ai).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        self.assertEqual(act_smt.Label, 'assign x = 1')
        v_val = one(act_ai).V_VAL[609]()
        self.assertFalse(v_val.isLValue)
        self.assertFalse(v_val.isImplicit)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.StartPosition, 12)
        self.assertEqual(v_val.EndPosition, 12)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'integer')
        
        v_val = one(act_ai).V_VAL[689]()
        self.assertTrue(v_val.isLValue)
        self.assertTrue(v_val.isImplicit)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.StartPosition, 8)
        self.assertEqual(v_val.EndPosition, 8)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'integer')
        
        v_tvl = one(v_val).V_TVL[801]()
        self.assertIsNotNone(v_tvl)
        
        v_var = one(v_tvl).V_VAR[805]()
        self.assertEqual(v_var.Name, 'x')
        self.assertTrue(v_var.Declared)
        
        s_dt = one(v_var).S_DT[848]()
        self.assertEqual(s_dt.Name, 'integer')
        
        v_trn = one(v_var).V_TRN[814]()
        self.assertIsNotNone(v_trn)
                
    @prebuild_docstring
    def test_positive_real(self):
        '''assign x = 1.1;'''
        act_ai = self.metamodel.select_one('ACT_AI')
        self.assertIsNotNone(act_ai)
        
        act_smt = one(act_ai).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ai).V_VAL[609]()
        self.assertFalse(v_val.isLValue)
        self.assertFalse(v_val.isImplicit)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.StartPosition, 12)
        self.assertEqual(v_val.EndPosition, 14)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'real')
        
        v_val = one(act_ai).V_VAL[689]()
        self.assertTrue(v_val.isLValue)
        self.assertTrue(v_val.isImplicit)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.StartPosition, 8)
        self.assertEqual(v_val.EndPosition, 8)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'real')
        
        v_tvl = one(v_val).V_TVL[801]()
        self.assertIsNotNone(v_tvl)
        
        v_var = one(v_tvl).V_VAR[805]()
        self.assertEqual(v_var.Name, 'x')
        self.assertTrue(v_var.Declared)
        
        s_dt = one(v_var).S_DT[848]()
        self.assertEqual(s_dt.Name, 'real')
        
        v_trn = one(v_var).V_TRN[814]()
        self.assertIsNotNone(v_trn)
        
    @prebuild_docstring
    def test_string(self):
        '''assign x = "Hello";'''
        act_ai = self.metamodel.select_one('ACT_AI')
        self.assertIsNotNone(act_ai)
        
        act_smt = one(act_ai).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ai).V_VAL[609]()
        self.assertFalse(v_val.isLValue)
        self.assertFalse(v_val.isImplicit)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.StartPosition, 12)
        self.assertEqual(v_val.EndPosition, 18)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'string')
        
        v_val = one(act_ai).V_VAL[689]()
        self.assertTrue(v_val.isLValue)
        self.assertTrue(v_val.isImplicit)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.StartPosition, 8)
        self.assertEqual(v_val.EndPosition, 8)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'string')
        
        v_tvl = one(v_val).V_TVL[801]()
        self.assertIsNotNone(v_tvl)
        
        v_var = one(v_tvl).V_VAR[805]()
        self.assertEqual(v_var.Name, 'x')
        self.assertTrue(v_var.Declared)
        
        s_dt = one(v_var).S_DT[848]()
        self.assertEqual(s_dt.Name, 'string')
        
        v_trn = one(v_var).V_TRN[814]()
        self.assertIsNotNone(v_trn)


if __name__ == "__main__":
    import logging
    import unittest
    
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
    
