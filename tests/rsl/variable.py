# encoding: utf-8
# Copyright (C) 2014 John Törnblom

from tests.rsl.utils import RSLTestCase
from tests.rsl.utils import evaluate

class TestVariables(RSLTestCase):

    @evaluate
    def testVariableWithKeywordName_Empty(self, rc):
        '''
        .assign empty = 1
        .exit "${empty}"
        '''
        self.assertEqual("1", rc)
        
    @evaluate
    def testVariableWithKeywordName_Where(self, rc):
        '''
        .assign where = 1
        .exit "${where}"
        '''
        self.assertEqual("1", rc)

        
    @evaluate
    def testVariableWithKeywordName_In(self, rc):
        '''
        .assign in = 1
        .exit "${in}"
        '''
        self.assertEqual("1", rc)



    @evaluate
    def testVariableWithTypeName(self, rc):
        '''
        .assign string = 1
        .exit "${string}"
        '''
        self.assertEqual("1", rc)

