# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from tests.test_bridgepoint.utils import PrebuildFunctionTestCase
from tests.test_bridgepoint.utils import prebuild_docstring

from xtuml import navigate_one as one


class TestConstLiterals(PrebuildFunctionTestCase):

    @prebuild_docstring
    def test_positive_integer(self):
        '''return 1;'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        act_smt = one(act_ret).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ret).V_VAL[668]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 8)
        self.assertEqual(v_val.endPosition, 8)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'integer')
        
        v_lin = one(v_val).V_LIN[801]()
        self.assertEqual(v_lin.Value, '1')

    @prebuild_docstring
    def test_negative_integer(self):
        '''return -1;'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        act_smt = one(act_ret).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ret).V_VAL[668]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 8)
        self.assertEqual(v_val.endPosition, 9)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'integer')
        
        v_uny = one(v_val).V_UNY[801]()
        self.assertEqual(v_uny.Operator, '-')

        v_val = one(v_uny).V_VAL[804]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 9)
        self.assertEqual(v_val.endPosition, 9)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'integer')
        
        v_lin = one(v_val).V_LIN[801]()
        self.assertEqual(v_lin.Value, '1')
        
    @prebuild_docstring
    def test_positive_real(self):
        '''return 1.1;'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        act_smt = one(act_ret).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ret).V_VAL[668]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 8)
        self.assertEqual(v_val.endPosition, 10)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'real')
        
        v_lrl = one(v_val).V_LRL[801]()
        self.assertEqual(v_lrl.Value, '1.1')
        
    @prebuild_docstring
    def test_negative_real(self):
        '''return -1.1;'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        act_smt = one(act_ret).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ret).V_VAL[668]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 8)
        self.assertEqual(v_val.endPosition, 11)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'real')
        
        v_uny = one(v_val).V_UNY[801]()
        self.assertEqual(v_uny.Operator, '-')

        v_val = one(v_uny).V_VAL[804]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 9)
        self.assertEqual(v_val.endPosition, 11)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'real')
        
        v_lrl = one(v_val).V_LRL[801]()
        self.assertEqual(v_lrl.Value, '1.1')
        
    @prebuild_docstring
    def test_string(self):
        '''return "Hello";'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        act_smt = one(act_ret).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ret).V_VAL[668]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 8)
        self.assertEqual(v_val.endPosition, 14)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'string')
        
        v_lst = one(v_val).V_LST[801]()
        self.assertEqual(v_lst.Value, 'Hello')
        
    @prebuild_docstring
    def test_empty_string(self):
        '''return "";'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        act_smt = one(act_ret).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ret).V_VAL[668]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 8)
        self.assertEqual(v_val.endPosition, 9)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'string')
        
        v_lst = one(v_val).V_LST[801]()
        self.assertEqual(v_lst.Value, '')
        
    @prebuild_docstring
    def test_true(self):
        '''return True;'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        act_smt = one(act_ret).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ret).V_VAL[668]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 8)
        self.assertEqual(v_val.endPosition, 11)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'boolean')
        
        v_lbo = one(v_val).V_LBO[801]()
        self.assertEqual(v_lbo.Value, 'TRUE')
        
    @prebuild_docstring
    def test_false_1(self):
        '''return False;'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        act_smt = one(act_ret).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ret).V_VAL[668]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 8)
        self.assertEqual(v_val.endPosition, 12)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'boolean')
        
        v_lbo = one(v_val).V_LBO[801]()
        self.assertEqual(v_lbo.Value, 'FALSE')
        
    @prebuild_docstring
    def test_false_2(self):
        '''return FaLsE;'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        act_smt = one(act_ret).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        v_val = one(act_ret).V_VAL[668]()
        self.assertEqual(v_val.isLValue, False)
        self.assertEqual(v_val.isImplicit, False)
        self.assertEqual(v_val.LineNumber, 1)
        self.assertEqual(v_val.startPosition, 8)
        self.assertEqual(v_val.endPosition, 12)
        
        s_dt = one(v_val).S_DT[820]()
        self.assertEqual(s_dt.Name, 'boolean')
        
        v_lbo = one(v_val).V_LBO[801]()
        self.assertEqual(v_lbo.Value, 'FALSE')
        
        
if __name__ == "__main__":
    import logging
    import unittest
    
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
    
