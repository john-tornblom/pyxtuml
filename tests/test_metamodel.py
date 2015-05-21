# encoding: utf-8
# Copyright (C) 2014-2015 John Törnblom

import unittest
import os

import xtuml


def expect_exception(exception):
    def test_decorator(fn):
        def test_decorated(self, *args, **kwargs):
            self.assertRaises(exception, fn, self, *args, **kwargs)
        return test_decorated
    return test_decorator


class TestModel(unittest.TestCase):
    resources = os.path.dirname(__file__) + os.sep + '..' + os.sep + 'resources'
    schema = resources + os.sep + 'ooaofooa_schema.sql'
    globals = resources + os.sep + 'Globals.xtuml'
    
    def setUp(self):
        self.metamodel = xtuml.load_metamodel([self.schema, self.globals])

    def tearDown(self):
        del self.metamodel

    def testSelectAny(self):
        m = self.metamodel
        self.assertNotEqual(m.select_any('S_DT'), None)

    def testSelectOne(self):
        m = self.metamodel
        self.assertNotEqual(m.select_one('S_DT'), None)
        
    def testSelectAnyWhere(self):
        m = self.metamodel
        inst = m.select_any('S_DT', lambda inst: inst.Name == 'void')
        self.assertEqual(inst.Name, 'void')
        
    def testNavOne(self):
        m = self.metamodel
        s_dt = m.select_any('S_DT', lambda inst: inst.name == 'void')
        pe_pe = xtuml.navigate_one(s_dt).PE_PE[8001](lambda inst: True)
        self.assertEqual(s_dt.DT_ID, pe_pe.Element_ID)
        
    def testNavMany(self):
        m = self.metamodel
        s_dt = m.select_many('S_DT')
        pe_pe = xtuml.navigate_many(s_dt).PE_PE[8001](lambda inst: True)
        self.assertEqual(len(s_dt), len(pe_pe))
   
    def testEmpty(self):
        m = self.metamodel
        self.assertTrue(m.empty(None))
        self.assertTrue(m.empty(m.select_many('S_DT', lambda inst: False)))
        self.assertFalse(m.empty(m.select_many('S_DT')))
        self.assertFalse(m.empty(m.select_any('S_DT')))

    def testNotEmpty(self):
        m = self.metamodel
        self.assertFalse(m.not_empty(None))
        self.assertFalse(m.not_empty(m.select_many('S_DT', lambda inst: False)))
        self.assertTrue(m.not_empty(m.select_many('S_DT')))
        self.assertTrue(m.not_empty(m.select_any('S_DT')))
        
    def testCardinality(self):
        m = self.metamodel
        self.assertEqual(0, m.cardinality(None))
        self.assertEqual(1, m.cardinality(m.select_any('S_DT')))
        
        q = m.select_many('S_DT', lambda inst: False)
        self.assertEqual(0, m.cardinality(q))
        
        q = m.select_many('S_DT')
        self.assertTrue(m.cardinality(q) > 0)
        
        x = 0
        for inst in q:
            x += 1
            
        self.assertEqual(x, len(q))
        self.assertEqual(x, m.cardinality(q))
        
    def testIsSet(self):
        m = self.metamodel

        q = m.select_many('S_DT', lambda inst: False)
        self.assertTrue(m.is_set(q))
        
        q = m.select_many('S_DT')
        self.assertTrue(m.is_set(q))

        q = m.select_any('S_DT')
        self.assertFalse(m.is_set(q))
        
        self.assertFalse(m.is_set(None))
                
    def testIsInstance(self):
        m = self.metamodel
        
        q = m.select_many('S_DT', lambda inst: False)
        self.assertFalse(m.is_instance(q))
        
        q = m.select_many('S_DT')
        self.assertFalse(m.is_instance(q))
        
        q = m.select_any('S_DT')
        self.assertTrue(m.is_instance(q))
        
        self.assertFalse(m.is_instance(None))

    def testQueryOrder(self):
        m = self.metamodel
        q = m.select_many('S_DT')
        
        length = m.cardinality(q)
        
        for index, inst in enumerate(q):
            self.assertEqual(index == 0, m.first(inst, q))
            self.assertEqual(index != 0, m.not_first(inst, q))
            self.assertEqual(index == length - 1, m.last(inst, q))
            self.assertEqual(index != length - 1, m.not_last(inst, q))

    def testIgnoreUndefinedClass(self):
        self.metamodel.ignore_undefined_classes = True
        self.metamodel.new('MY_UNDEFINED_CLASS')
        
    @expect_exception(xtuml.ModelException)
    def testUndefinedClass(self):
        self.metamodel.new('MY_UNDEFINED_CLASS')
        

        
            
if __name__ == "__main__":
    unittest.main()

