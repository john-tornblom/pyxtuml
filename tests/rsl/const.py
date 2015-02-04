# encoding: utf-8
# Copyright (C) 2014 John Törnblom

from tests.rsl.utils import RSLTestCase
from tests.rsl.utils import evaluate

class TestConstLiterals(RSLTestCase):

    @evaluate
    def testPositiveInteger(self, rc):
        '.exit 1'
        self.assertEqual(1, rc)

    @evaluate
    def testNegativeInteger(self, rc):
        '.exit -1'
        self.assertEqual(-1, rc)

    @evaluate
    def testPositiveReal(self, rc):
        '''
        .exit 1.1
        '''
        self.assertEqual(1.1, rc)
        
    @evaluate
    def testNegativeReal(self, rc):
        '''
        .exit -1.1
        '''
        self.assertEqual(-1.1, rc)

    @evaluate
    def testString(self, rc):
        '.exit "Hello"'
        self.assertEqual("Hello", rc)


    @evaluate
    def testEmptyString(self, rc):
        '''
        .exit ""
        '''
        self.assertEqual("", rc)
        
