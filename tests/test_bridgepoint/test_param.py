# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from tests.test_bridgepoint.utils import PrebuildFunctionTestCase
from tests.test_bridgepoint.utils import prebuild_docstring

from xtuml import navigate_one as one
from xtuml import relate


class TestFunctionWithParameters(PrebuildFunctionTestCase):

    def setUp(self):
        PrebuildFunctionTestCase.setUp(self)
        s_sync = self.metamodel.select_any('S_SYNC')
        p1 = self.metamodel.new('S_SPARM', Name='P1')
        p2 = self.metamodel.new('S_SPARM', Name='p2')
        relate(p1, s_sync, 24)
        relate(p2, s_sync, 24)
        relate(p1, p2, 54, 'succeeds')
        
        s_dt = self.metamodel.select_any('S_DT', lambda sel: sel.Name == 'boolean')
        relate(p1, s_dt, 26)
        relate(p2, s_dt, 26)

    @prebuild_docstring
    def test_read_P1(self):
        '''return param.P1;'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        p1 = one(act_ret).V_VAL[668].V_PVL[801].S_SPARM[832]()
        self.assertEqual(p1.Name, 'P1')
        
    @prebuild_docstring
    def test_read_p2(self):
        '''return param.p2;'''
        act_ret = self.metamodel.select_one('ACT_RET')
        self.assertIsNotNone(act_ret)
        
        p2 = one(act_ret).V_VAL[668].V_PVL[801].S_SPARM[832]()
        self.assertEqual(p2.Name, 'p2')
        

if __name__ == "__main__":
    import logging
    import unittest
    
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

