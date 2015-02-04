# encoding: utf-8
# Copyright (C) 2014 John Törnblom

from tests.rsl.utils import RSLTestCase
from tests.rsl.utils import evaluate

class TestLoop(RSLTestCase):

    @evaluate
    def testWhileLoop(self, rc):
        '''
        .assign x = 10
        .while (x > 0)
            .assign x = x - 1
        .end while
        .exit x
        '''
        self.assertEqual(0, rc)
        
    @evaluate
    def testWhileLoopBreak(self, rc):
        '''
        .assign x = 10
        .while (x > 0)
            .if (x == 5)
                .break while
            .end if
            .assign x = x - 1
        .end while
        .exit x
        '''
        self.assertEqual(5, rc)
        
    def testForLoop(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .assign x = x + 1
        .end for
        .exit x
        '''
        
        for i in range(0, 10):
            rc = self.eval_text(text)
            self.assertEqual(i, rc)
            self.metamodel.new('A')
        
    def testForLoopBreak(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .if (x == 3)
                .break for
            .end if
            .assign x = x + 1
        .end for
        .exit x
        '''

        for _ in range(0, 10):
            self.metamodel.new('A')
            
        rc = self.eval_text(text)
        self.assertEqual(3, rc)


    def testFirstInLoop(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .if (first a_set)
                .assign x = x + 1
            .end if
        .end for
        .exit x
        '''
        
        for _ in range(0, 10):
            self.metamodel.new('A')
            
        rc = self.eval_text(text)
        self.assertEqual(1, rc)


    def testNotFirstInLoop(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .if (not_first a_set)
                .assign x = x + 1
            .end if
        .end for
        .exit x
        '''
        
        for _ in range(0, 10):
            self.metamodel.new('A')
            
        rc = self.eval_text(text)
        self.assertEqual(9, rc)
        
        
    def testLastInLoop(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .if (last a_set)
                .assign x = x + 1
            .end if
        .end for
        .exit x
        '''
        
        for _ in range(0, 10):
            self.metamodel.new('A')
            
        rc = self.eval_text(text)
        self.assertEqual(1, rc)
        

    def testNotLastInLoop(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .if (not_last a_set)
                .assign x = x + 1
            .end if
        .end for
        .exit x
        '''
        
        for _ in range(0, 10):
            self.metamodel.new('A')
            
        rc = self.eval_text(text)
        self.assertEqual(9, rc)
        


