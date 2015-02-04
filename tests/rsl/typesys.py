# encoding: utf-8
# Copyright (C) 2014 John Törnblom

from tests.rsl.utils import RSLTestCase
from xtuml.rsl.runtime import RuntimeException

class TestTypeSys(RSLTestCase):


    def testInvoke_Parameter(self):

        def f(ty, val):
            return self.eval_text('''
                .function f
                    .param %s x
                .end function
                .invoke f(%s)
                .exit true''' % (ty, val), 'TestTypeSys.testInvoke_Parameter(%s, %s)' % (ty, val))
        
        self.assertTrue(f('boolean', 'true'))
        self.assertTrue(f('boolean', 'false'))
        self.assertTrue(f('integer', '1'))
        self.assertTrue(f('integer', '-1'))
        self.assertTrue(f('string', '""'))
        self.assertTrue(f('string', '"Hello"'))
        self.assertTrue(f('real', '0.0'))
        self.assertTrue(f('real', '-0.1'))
        self.assertTrue(f('real', '1'))
        
        self.assertIsInstance(f('boolean', '1'), RuntimeException)
        self.assertIsInstance(f('integer', '1.1'), RuntimeException)
        self.assertIsInstance(f('string', 'true'), RuntimeException)
        self.assertIsInstance(f('frag_ref', '0'), RuntimeException)


    def testInvoke_FragmentParameter(self):

        def f(ty):
            return self.eval_text('''
                .function g
                    .assign attr_result = True
                .end function
                .function f
                    .param %s x
                .end function
                .invoke value = g()
                .invoke f(value)
                .exit true''' % ty, 
                'TestTypeSys.testInvoke_FragmentParameter(%s)' % ty)
        
        self.assertTrue(f('frag_ref'))
        
        self.assertIsInstance(f('boolean'), RuntimeException)
        self.assertIsInstance(f('integer'), RuntimeException)
        self.assertIsInstance(f('real'), RuntimeException)
        self.assertIsInstance(f('string'), RuntimeException)
