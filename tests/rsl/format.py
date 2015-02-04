# encoding: utf-8
# Copyright (C) 2014 John Törnblom

from tests.rsl.utils import RSLTestCase
from tests.rsl.utils import evaluate

class TestConstLiterals(RSLTestCase):

    @evaluate
    def testUpperCase(self, rc):
        '''
        .assign x = "hello"
        .exit "$U{x}"
        '''
        self.assertEqual("HELLO", rc)


    @evaluate
    def testLowerCase(self, rc):
        '''
        .assign x = "HELlo"
        .exit "$L{x}"
        '''
        self.assertEqual("hello", rc)


    @evaluate
    def testCapitalize(self, rc):
        '''
        .assign x = "hello"
        .exit "$C{x}"
        '''
        self.assertEqual("Hello", rc)


    @evaluate
    def testUnderscore(self, rc):
        '''
        .assign x = "hello world"
        .exit "$_{x}"
        '''
        self.assertEqual("hello_world", rc)


    @evaluate
    def testcOrba(self, rc):
        '''
        .assign x = "HelLO woRLd"
        .exit "$o{x}"
        '''
        self.assertEqual("helloWorld", rc)


    @evaluate
    def testcOrbaWithUnderline(self, rc):
        '''
        .assign x = "Hello_world!"
        .exit "$o{x}"
        '''
        self.assertEqual("helloWorld", rc)
        
        
    @evaluate
    def testcOrbaWithEmptyString(self, rc):
        '''
        .assign x = ""
        .exit "$o{x}"
        '''
        self.assertEqual("", rc)
        
        
                
    @evaluate
    def testExampleU(self, rc):
        '''
        .assign x = "Example Text"
        .exit "$u{x}"
        '''
        self.assertEqual("EXAMPLE TEXT", rc)
        
        
    @evaluate
    def testExampleU_(self, rc):
        '''
        .assign x = "Example Text"
        .exit "$u_{x}"
        '''
        self.assertEqual("EXAMPLE_TEXT", rc)

        
    @evaluate
    def testExampleUR(self, rc):
        '''
        .assign x = "Example Text"
        .exit "$ur{x}"
        '''
        self.assertEqual("EXAMPLETEXT", rc)


    @evaluate
    def testExampleC(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$c{x}"
        '''
        self.assertEqual("Example Text", rc)
        

    @evaluate
    def testExampleC_(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$c_{x}"
        '''
        self.assertEqual("Example_Text", rc)
        
        
    @evaluate
    def testExampleCR(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$cr{x}"
        '''
        self.assertEqual("ExampleText", rc)
        
        
    @evaluate
    def testExampleL(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$l{x}"
        '''
        self.assertEqual("example text", rc)
        
        
    @evaluate
    def testExampleL_(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$l_{x}"
        '''
        self.assertEqual("example_text", rc)
        
        
    @evaluate
    def testExampleLR(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$lr{x}"
        '''
        self.assertEqual("exampletext", rc)
        
        
    @evaluate
    def testExampleO(self, rc):
        '''
        .assign x = "ExamplE@34 TExt"
        .exit "$o{x}"
        '''
        self.assertEqual("example34Text", rc)
        
        
                
        