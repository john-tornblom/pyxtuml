# encoding: utf-8
# Copyright (C) 2014 John Törnblom

from tests.rsl.utils import RSLTestCase
from tests.rsl.utils import evaluate
from xtuml.rsl.runtime import RuntimeException

class TestInvoke(RSLTestCase):

    @evaluate
    def testInvokeEmptyFunction(self, rc):
        '''
        .function f
        .end function
        .invoke f()
        .exit 1
        '''
        self.assertEqual(1, rc)
        
    @evaluate
    def testInvokeDotNamedFunction(self, rc):
        '''
        .function module.f
        .exit 1
        .end function
        .invoke module.f()
        .exit 0
        '''
        self.assertEqual(1, rc)
    
    @evaluate
    def testInvokeWithExit(self, rc):
        '''
        .function f
            .exit 1
        .end function
        .invoke f()
        .exit 0
        '''
        self.assertEqual(1, rc)

    @evaluate
    def testInvokeWithParameter(self, rc):
        '''
        .function f
            .param integer x
            .exit x + 1
        .end function
        .invoke f(1)
        .exit 0
        '''
        self.assertEqual(2, rc)

    @evaluate
    def testInvokeWithParameterAndComments(self, rc):
        '''
        .function f .// integer
            .param integer x .// some comment
            .// begin body
            .exit x + 1
        .end function
        .invoke f(1)
        .exit 0
        '''
        self.assertEqual(2, rc)
        
    @evaluate
    def testParameterOrder(self, rc):
        '''
        .function f
            .param integer x
            .param integer y
            .param integer z
            .exit x
        .end function
        .invoke f(1, 2, 3)
        .exit 0
        '''
        self.assertEqual(1, rc)

    @evaluate
    def testInvokeWithReturnValue(self, rc):
        '''
        .function f
            .assign attr_value = 1
        .end function
        .invoke res = f()
        .exit res.value
        '''
        self.assertEqual(1, rc)

    @evaluate
    def testInvokeDotNamedFunctionWithReturnValue(self, rc):
        '''
        .function module.f
            .assign attr_value = 1
        .end function
        .invoke res = module.f()
        .exit res.value
        '''
        self.assertEqual(1, rc)

    @evaluate
    def testInvokeWithReturnValues(self, rc):
        '''
        .function f
            .assign attr_x = 1
            .assign attr_y = 2
        .end function
        .invoke res = f()
        .if (res.x != 1)
            .exit 1
        .end if
        .if (res.y != 2)
            .exit 1
        .end if
        .exit 0
        '''
        self.assertEqual(0, rc)


    @evaluate
    def testInvokeFromOtherBody(self, rc):
        '''
        ..function f
            ..assign attr_x = 1
            ..assign attr_y = 2
        ..end function
        .emit to file "/tmp/RSLTestCase"
        .include "/tmp/RSLTestCase"
        .invoke res = f()
        .if (res.x != 1)
            .exit 1
        .end if
        .if (res.y != 2)
            .exit 1
        .end if
        .exit 0
        '''
        self.assertEqual(0, rc)


    @evaluate
    def testInvokeUndefinedFunction(self, rc):
        '''
        .invoke res = f()
        .exit 0
        '''
        self.assertIsInstance(rc, RuntimeException)
        
