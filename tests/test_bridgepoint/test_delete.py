# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from tests.test_bridgepoint.utils import PrebuildFunctionTestCase
from tests.test_bridgepoint.utils import prebuild_docstring

from xtuml import navigate_one as one
from xtuml import relate


class TestDelete(PrebuildFunctionTestCase):

    def setUp(self):
        PrebuildFunctionTestCase.setUp(self)
        pe_pe = self.metamodel.new('PE_PE')
        o_obj = self.metamodel.new('O_OBJ', Key_Lett='A')
        relate(pe_pe, o_obj, 8001)
    
    @prebuild_docstring
    def test_delete_object(self):
        '''
        create object instance inst of A;
        delete object instance inst;
        '''
        act_del = self.metamodel.select_one('ACT_DEL')
        
        act_smt = one(act_del).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)

        v_var = one(act_del).V_VAR[634]()
        self.assertEqual(v_var.Name, 'inst')
        
        
if __name__ == "__main__":
    import logging
    import unittest
    
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
    
