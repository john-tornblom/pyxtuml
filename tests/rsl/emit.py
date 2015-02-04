# encoding: utf-8
# Copyright (C) 2014 John Törnblom

from tests.rsl.utils import RSLTestCase
from tests.rsl.utils import evaluate


class TestEmit(RSLTestCase):

    @evaluate
    def testEmitHelloWorld(self, rc):
        '''Hello world
        .emit to file "/tmp/RSLTestCase"'''
        
        with open("/tmp/RSLTestCase") as f:
            self.assertRegexpMatches(f.read(), "Hello world\n")
        

    def testEmitWithoutLinebreak_Case1(self):
        text = 'Hello world' + '\\' + '\n' 
        text+= '.emit to file "/tmp/RSLTestCase"' 
        
        self.eval_text(text)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "Hello world")
            
            
    def testEmitWithoutLinebreak_Case2(self):
        text = 'Hello world' + '\\' + '\\' + '\\' + '\n' 
        text+= '.emit to file "/tmp/RSLTestCase"' 
        
        self.eval_text(text)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "Hello world\\")
    
    def testEmitEscapedBackslash(self):
        text = 'Hello world' + '\\' + '\\' + '\n' 
        text+= '.emit to file "/tmp/RSLTestCase"' 
        
        self.eval_text(text)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "Hello world\\\n")
    
    @evaluate
    def testEmitComment(self, rc):
        '''.//Hello world
        .comment No comment
        .emit to file "/tmp/RSLTestCase"'''
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "")
        
    @evaluate
    def testEmitFlush(self, rc):
        '''Hello world
        .emit to file "/tmp/RSLTestCase"
        .emit to file "/tmp/RSLTestCase"'''
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "")
        
    @evaluate
    def testIncludeAfterEmit(self, rc):
        '''..exit 1
        .emit to file "/tmp/RSLTestCase"
        .include "/tmp/RSLTestCase"
        .exit 0
        '''
        self.assertEqual(1, rc)
            

    @evaluate
    def testEmitAfterClear(self, rc):
        '''
        Hello world
        .clear
        .emit to file "/tmp/RSLTestCase"
        '''
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "")
    
    @evaluate
    def testEmitFromFunction(self, rc):
        '''
        .function f
Hello world!
        .end function
        .invoke rc = f()
        .emit to file "/tmp/RSLTestCase"
        .exit rc.body
        '''
        
        self.assertEqual("Hello world!\n", rc)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "\n")

