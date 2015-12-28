# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from tests.test_bridgepoint.utils import PrebuildFunctionTestCase
from tests.test_bridgepoint.utils import prebuild_docstring

from xtuml import navigate_one as one


class TestControl(PrebuildFunctionTestCase):

    @prebuild_docstring
    def testControlStop(self):
        '''control stop;'''
        act_ctl = self.metamodel.select_one('ACT_CTL')
        self.assertIsNotNone(act_ctl)
        
        act_smt = one(act_ctl).ACT_SMT[603]()
        self.assertIsNotNone(act_smt)
        

if __name__ == "__main__":
    import logging
    import unittest
    
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

