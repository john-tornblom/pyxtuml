# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from tests.test_bridgepoint.utils import PrebuildFunctionTestCase
from tests.test_bridgepoint.utils import prebuild_docstring

from xtuml import navigate_one as one
from xtuml import relate


class TestForEach(PrebuildFunctionTestCase):
    
    def setUp(self):
        PrebuildFunctionTestCase.setUp(self)
        pe_pe = self.metamodel.new('PE_PE')
        o_obj = self.metamodel.new('O_OBJ', Key_Lett='A')
        relate(pe_pe, o_obj, 8001)
        
    @prebuild_docstring
    def test_for_each_loop(self):
        '''
        create object instance of A;
        create object instance of A;       
        select many a_set from instances of A;
        for each a in a_set
        end for;
        '''
        act_for = self.metamodel.select_one('ACT_FOR')
        self.assertTrue(act_for.is_implicit)
        
        act_smt = one(act_for).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        
        act_blk = one(act_for).ACT_BLK[605]()
        self.assertIsNotNone(act_blk)
        
        v_var = one(act_for).V_VAR[614]()
        self.assertEqual(v_var.Name, 'a')
        
        v_var = one(act_for).V_VAR[652]()
        self.assertEqual(v_var.Name, 'a_set')

        o_obj = one(act_for).O_OBJ[670]()
        self.assertEqual(o_obj.Key_Lett, 'A')

        
if __name__ == "__main__":
    import logging
    import unittest
    
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

