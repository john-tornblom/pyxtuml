# encoding: utf-8
# Copyright (C) 2014 John Törnblom

from tests.rsl.utils import RSLTestCase
from tests.rsl.utils import evaluate

class TestBinOp(RSLTestCase):

    @evaluate
    def testPlus(self, rc):
        '.exit 1 + 1'
        self.assertEqual(2, rc)
        
    @evaluate
    def testMinus(self, rc):
        '.exit 1 - 1'
        self.assertEqual(0, rc)

    @evaluate
    def testUnaryMinus(self, rc):
        '.exit 1 - -1'
        self.assertEqual(2, rc)
        
    @evaluate
    def testMult(self, rc):
        '.exit 2 * 2'
        self.assertEqual(4, rc)
        
    @evaluate
    def testDiv(self, rc):
        '.exit 10 / 2'
        self.assertEqual(5, rc)
        
    @evaluate
    def testLessTrue(self, rc):
        '.exit 0 < 1'
        self.assertTrue(rc)
        
    @evaluate
    def testLessFalse(self, rc):
        '.exit 0 < 0'
        self.assertFalse(rc)
        
    @evaluate
    def testLessEqTrue(self, rc):
        '.exit 1 <= 1'
        self.assertTrue(rc)
        
    @evaluate
    def testLessEqFalse(self, rc):
        '.exit 2 <= 1'
        self.assertFalse(rc)
        
    @evaluate
    def testNotEqFalse(self, rc):
        '.exit 1 != 1'
        self.assertFalse(rc)
    
    @evaluate
    def testGreatEqFalse(self, rc):
        '.exit 1 >= 2'
        self.assertFalse(rc)
        
    @evaluate
    def testGreatEqTrue(self, rc):
        '.exit 3 >= 2'
        self.assertTrue(rc)
        
    @evaluate
    def testNotEqTrue(self, rc):
        '.exit 0 != 1'
        self.assertTrue(rc)
        
    @evaluate
    def testEqFalse(self, rc):
        '.exit 0 == 1'
        self.assertFalse(rc)
        
    @evaluate
    def testEqTrue(self, rc):
        '.exit 1 == 1'
        self.assertTrue(rc)
        

    @evaluate
    def testGroupedBinOp(self, rc):
        '''
        .assign x = (1 + 1)
        .exit x
        '''
        self.assertEqual(2, rc)
        

    @evaluate
    def testChainedBinOp(self, rc):
        '''
        .assign x = (1 + 1) + 1
        .exit x
        '''
        self.assertEqual(3, rc)

    @evaluate
    def testChainedUnaryOp(self, rc):
        '''
        .assign x = not (1 == 1)
        .exit x
        '''
        self.assertEqual(False, rc)

    @evaluate
    def testAndBinOpTrue(self, rc):
        '''
        .exit True and True
        '''
        self.assertTrue(rc)
        
    @evaluate
    def testAndBinOpFalse(self, rc):
        '''
        .exit True and False
        '''
        self.assertFalse(rc)
        
    @evaluate
    def testOrBinOpTrue(self, rc):
        '''
        .exit True or False
        '''
        self.assertTrue(rc)
        
    @evaluate
    def testOrBinOpFalse(self, rc):
        '''
        .exit False or False
        '''
        self.assertFalse(rc)
        
    def testBinOpPipe(self):
        self.metamodel.define_class('A', [('Name', 'string')])

        text = '''
        .create object instance a1 of A
        .create object instance a2 of A
        .create object instance a3 of A
        .assign a1.Name = "A1"
        .assign a2.Name = "A2"
        .assign a3.Name = "A3"
        
        .select any a1_set from instances of A where (selected.Name == "A1")
        .select any a2_set from instances of A where (selected.Name == "A2")
        
        .assign a_set = a1_set | a2_set
        .exit cardinality a_set
        '''
        rc = self.eval_text(text)
        self.assertEqual(2, rc)
    
        text = '''
        
        .select any a1_set from instances of A where (selected.Name == "A1")
        .select many a_set from instances of A
        
        .assign a_set = a1_set | a_set
        .exit cardinality a_set
        '''
        rc = self.eval_text(text)
        self.assertEqual(3, rc)
        
    def testBinOpAmpesand(self):
        self.metamodel.define_class('A', [('Name', 'string')])

        text = '''
        .create object instance a1 of A
        .create object instance a2 of A
        .create object instance a3 of A
        .assign a1.Name = "A1"
        .assign a2.Name = "A2"
        .assign a3.Name = "A3"
        
        .select any a1_set from instances of A where (selected.Name == "A1")
        .select any a2_set from instances of A where (selected.Name == "A2")
        
        .assign a_set = a1_set & a2_set
        .exit cardinality a_set
        '''
        rc = self.eval_text(text)
        self.assertEqual(0, rc)
    
        text = '''
        .select many not_a1_set from instances of A where (selected.Name != "A1")
        .select many not_a2_set from instances of A where (selected.Name != "A2")
        
        .assign a3_set = not_a1_set & not_a2_set
        .exit cardinality a3_set
        '''
        rc = self.eval_text(text)
        self.assertEqual(1, rc)
        

    def testInstancePlusInstance(self):
        self.metamodel.define_class('A', [('Name', 'string')])

        text = '''
        .create object instance a1 of A
        .create object instance a2 of A
        .assign a1.Name = "A1"
        .assign a2.Name = "A2"
        
        .assign a_set = a1 + a2
        .exit cardinality a_set
        '''
        rc = self.eval_text(text)
        self.assertEqual(2, rc)
        
    def testInstanceMinusInstance(self):
        self.metamodel.define_class('A', [('Name', 'string')])

        text = '''
        .create object instance a1 of A
        .create object instance a2 of A
        .assign a1.Name = "A1"
        .assign a2.Name = "A2"
        
        .assign a_set = a1 - a2
        .exit cardinality a_set
        '''
        rc = self.eval_text(text)
        self.assertEqual(1, rc)
        
    def testInstanceMinusSameInstance(self):
        self.metamodel.define_class('A', [('Name', 'string')])

        text = '''
        .create object instance a1 of A
        .assign a1.Name = "A1"
        
        .assign a_set = a1 - a1
        .exit cardinality a_set
        '''
        rc = self.eval_text(text)
        self.assertEqual(0, rc)
        
