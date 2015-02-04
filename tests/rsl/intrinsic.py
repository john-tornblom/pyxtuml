# encoding: utf-8
# Copyright (C) 2014 John Törnblom

from tests.rsl.utils import RSLTestCase
from tests.rsl.utils import evaluate

import os

class TestIntrinsics(RSLTestCase):

    @evaluate
    def test_GET_ENV_VAR(self, rc):
        '''
        .invoke rc = GET_ENV_VAR("PATH")
        .exit rc.result
        '''
        self.assertEqual(os.environ['PATH'], rc)


    @evaluate
    def test_GET_ENV_VAR_failure(self, rc):
        '''
        .invoke rc = GET_ENV_VAR("UNKNOWN_PATH")
        .exit rc.success
        '''
        self.assertFalse(rc)

    @evaluate
    def test_PUT_ENV_VAR(self, rc):
        '''
        .invoke rc = PUT_ENV_VAR("MY_PATH", "test")
        .exit rc.success
        '''
        self.assertTrue(rc)
        self.assertEqual(os.environ["MY_PATH"], "test")
    
    @evaluate
    def test_FILE_READ_WRITE(self, rc):
        '''
        .invoke rc = FILE_WRITE("/tmp/RSLTestCase", "Hello world!")
        .if ( not rc.success )
            .exit ""
        .end if
        .invoke rc = FILE_READ("/tmp/RSLTestCase")
        .if ( not rc.success )
            .exit ""
        .end if
        .exit rc.result
        '''
        self.assertEqual(rc, "Hello world!\n")
    
    
    @evaluate
    def test_FILE_READ_error(self, rc):
        '''
        .invoke rc = FILE_READ("/")
        .exit rc.success
        '''
        self.assertFalse(rc)
        
    @evaluate
    def test_FILE_Write_error(self, rc):
        '''
        .invoke rc = FILE_WRITE("/", "TEST")
        .exit rc.success
        '''
        self.assertFalse(rc)
        
    @evaluate
    def test_SHELL_COMMAND_true(self, rc):
        '''
        .invoke rc = SHELL_COMMAND("true")
        .exit rc.result
        '''
        self.assertEqual(0, rc)
    
    @evaluate
    def test_SHELL_COMMAND_false(self, rc):
        '''
        .invoke rc = SHELL_COMMAND("false")
        .exit rc.result
        '''
        self.assertEqual(1, rc)
        
    @evaluate
    def test_INTEGER_TO_STRING(self, rc):
        '''
        .invoke rc = INTEGER_TO_STRING(1)
        .exit rc.result
        '''
        self.assertEqual("1", rc)
        
    @evaluate
    def test_REAL_TO_STRING(self, rc):
        '''
        .invoke rc = REAL_TO_STRING(1.1)
        .exit rc.result
        '''
        self.assertEqual("1.1", rc)
    
    @evaluate
    def test_BOOLEAN_TO_STRING(self, rc):
        '''
        .invoke rc = BOOLEAN_TO_STRING(False)
        .exit rc.result
        '''
        self.assertEqual("FALSE", rc)
    
    @evaluate
    def test_STRING_TO_INTEGER(self, rc):
        '''
        .invoke rc = STRING_TO_INTEGER("1")
        .exit rc.result
        '''
        self.assertEqual(1, rc)
        
    @evaluate
    def test_STRING_TO_REAL(self, rc):
        '''
        .invoke rc = STRING_TO_REAL("1.1")
        .exit rc.result
        '''
        self.assertEqual(1.1, rc)
    