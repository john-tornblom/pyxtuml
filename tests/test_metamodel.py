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
    
    @classmethod
    def setUpClass(cls):
        resources = os.path.dirname(__file__) + os.sep + '..' + os.sep + 'resources'
        schema = resources + os.sep + 'ooaofooa_schema.sql'
        globs = resources + os.sep + 'Globals.xtuml'
    
        cls.loader = xtuml.load.ModelLoader()
        cls.loader.build_parser()
        cls.loader.filename_input(schema)
        cls.loader.filename_input(globs)
 
    def setUp(self):
        self.metamodel = self.loader.build_metamodel()

    def tearDown(self):
        del self.metamodel

    def testSelectAny(self):
        m = self.metamodel
        self.assertNotEqual(m.select_any('S_DT'), None)

    def testSelectOne(self):
        m = self.metamodel
        self.assertNotEqual(m.select_one('S_DT'), None)
        
    def testSelectMany(self):
        m = self.metamodel
        q = m.select_many('S_DT')
        self.assertIsInstance(q, xtuml.QuerySet)
        self.assertTrue(len(q) > 0)
        
        q = m.select_many('S_EDT')
        self.assertIsInstance(q, xtuml.QuerySet)
        self.assertTrue(len(q) == 0)
        
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
        self.assertTrue(len(m.select_many('S_DT', lambda inst: False)) == 0)
        self.assertFalse(len(m.select_many('S_DT')) == 0)
       
    def testCardinality(self):
        m = self.metamodel
        
        q = m.select_many('S_DT', lambda inst: False)
        self.assertEqual(0, len(q))
        
        q = m.select_many('S_DT')
        self.assertTrue(len(q) > 0)
        
        x = 0
        for _ in q:
            x += 1
            
        self.assertEqual(x, len(q))
        
    def testIsSet(self):
        m = self.metamodel

        q = m.select_many('S_DT', lambda inst: False)
        self.assertIsInstance(q, xtuml.QuerySet)
        
        q = m.select_many('S_DT')
        self.assertIsInstance(q, xtuml.QuerySet)
                
    def testIsInstance(self):
        m = self.metamodel
        
        q = m.select_any('S_DT')
        self.assertIsInstance(q, xtuml.BaseObject)

    def testQueryOrder(self):
        m = self.metamodel
        q = m.select_many('S_DT')
        
        length = len(q)
        for index, inst in enumerate(q):
            self.assertEqual(index == 0, inst == q.first)
            self.assertEqual(index != 0, inst != q.first)
            self.assertEqual(index == length - 1, inst == q.last)
            self.assertEqual(index != length - 1, inst != q.last)

    def testIgnoreUndefinedClass(self):
        self.metamodel.ignore_undefined_classes = True
        self.metamodel.new('MY_UNDEFINED_CLASS')
        
    @expect_exception(xtuml.ModelException)
    def testUndefinedClass(self):
        self.metamodel.new('MY_UNDEFINED_CLASS')
        
    def testRelate(self):
        s_edt = self.metamodel.new('S_EDT')
        s_dt = self.metamodel.new('S_DT')
        
        xtuml.relate(s_dt, s_edt, 17)
        self.assertEqual(s_edt, xtuml.navigate_one(s_dt).S_EDT[17]())

    def testRelateReflexive1(self):
        inst1 = self.metamodel.new('ACT_SMT')
        inst2 = self.metamodel.new('ACT_SMT')
        
        xtuml.relate(inst1, inst2, 661, 'precedes')
        self.assertEqual(inst2, xtuml.navigate_one(inst1).ACT_SMT[661, 'succeeds']())
        self.assertEqual(inst1, xtuml.navigate_one(inst2).ACT_SMT[661, 'precedes']())
        
    def testRelateReflexive2(self):
        inst1 = self.metamodel.new('ACT_SMT')
        inst2 = self.metamodel.new('ACT_SMT')
        
        xtuml.relate(inst2, inst1, 661, 'succeeds')
        self.assertEqual(inst2, xtuml.navigate_one(inst1).ACT_SMT[661, 'succeeds']())
        self.assertEqual(inst1, xtuml.navigate_one(inst2).ACT_SMT[661, 'precedes']())
        
    @expect_exception(xtuml.ModelException)
    def testRelateReflexiveWithoutPhrase(self):
        inst1 = self.metamodel.new('ACT_SMT')
        inst2 = self.metamodel.new('ACT_SMT')
        
        xtuml.relate(inst1, inst2, 661, '<invalid phrase>')
        
    def testRelateInvertedOrder(self):
        s_edt = self.metamodel.new('S_EDT')
        s_dt = self.metamodel.new('S_DT')
        xtuml.relate(s_edt, s_dt, 17)
        self.assertEqual(s_edt, xtuml.navigate_one(s_dt).S_EDT[17]())
    
    @expect_exception(xtuml.ModelException)
    def testRelateInvalidRelId(self):
        s_edt = self.metamodel.new('S_EDT')
        s_dt = self.metamodel.new('S_DT')
        xtuml.relate(s_edt, s_dt, 0)
        self.assertEqual(s_edt, xtuml.navigate_one(s_dt).S_EDT[17]())
        
    def testUnrelate(self):
        s_dt = self.metamodel.select_any('S_DT', lambda inst: inst.name == 'integer')
        s_cdt = xtuml.navigate_one(s_dt).S_CDT[17]()
        self.assertEqual(s_cdt.Core_Typ, 2)
        xtuml.unrelate(s_dt, s_cdt, 17)
        self.assertEqual(s_dt.Name, 'integer')
        self.assertEqual(s_cdt.Core_Typ, 2)
        self.assertIsNone(xtuml.navigate_one(s_dt).S_CDT[17]())

    def testRelateInWrongOrder(self):
        s_ee = self.metamodel.new('S_EE')
        pe_pe = self.metamodel.new('PE_PE')
        EE_ID = s_ee.EE_ID
        Element_ID = pe_pe.Element_ID
        xtuml.relate(s_ee, pe_pe, 8001)
        self.assertNotEqual(EE_ID, s_ee.EE_ID)
        self.assertEqual(Element_ID, pe_pe.Element_ID)


    def testRelateTopDown(self):
        m = self.metamodel
        s_dt = m.select_one('S_DT', lambda selected: selected.Name == 'string')
        s_bparm = m.new('S_BPARM', Name='My_Parameter')
        s_ee = m.new('S_EE', Name='My_External_Entity', Key_Lett='My_External_Entity')
        pe_pe = m.new('PE_PE', Visibility=True, type=5)
        s_brg = m.new('S_BRG', Name='My_Bridge_Operation')

        xtuml.relate(s_ee, pe_pe, 8001)
        xtuml.relate(s_brg, s_ee, 19)
        xtuml.relate(s_brg, s_dt, 20)
        xtuml.relate(s_bparm, s_brg, 21)
        xtuml.relate(s_bparm, s_dt, 22)
            
        inst = xtuml.navigate_any(pe_pe).S_EE[8001].S_BRG[19].S_BPARM[21]()
        self.assertEqual(inst, s_bparm)
        
    def testRelateBottomUp(self):
        m = self.metamodel
        s_dt = m.select_one('S_DT', lambda selected: selected.Name == 'string')
        s_bparm = m.new('S_BPARM', Name='My_Parameter')
        s_ee = m.new('S_EE', Name='My_External_Entity', Key_Lett='My_External_Entity')
        pe_pe = m.new('PE_PE', Visibility=True, type=5)
        s_brg = m.new('S_BRG', Name='My_Bridge_Operation')
        
        xtuml.relate(s_bparm, s_dt, 22)
        xtuml.relate(s_bparm, s_brg, 21)
        xtuml.relate(s_brg, s_dt, 20)
        xtuml.relate(s_brg, s_ee, 19)
        xtuml.relate(s_ee, pe_pe, 8001)
            
        inst = xtuml.navigate_any(pe_pe).S_EE[8001].S_BRG[19].S_BPARM[21]()
        self.assertEqual(inst, s_bparm)
    
        
        
class TestDefineModel(unittest.TestCase):
    
 
    def setUp(self):
        self.metamodel = xtuml.MetaModel()

    def tearDown(self):
        del self.metamodel

    def testReflexive(self):
        self.metamodel.define_class('A', [('Id', 'unique_id'),
                                          ('Next_Id', 'unique_id'),
                                          ('Name', 'string')])
        
        endpint1 = xtuml.SingleAssociationLink('A', ids=['Id'], phrase='prev')
        endpint2 = xtuml.SingleAssociationLink('A', ids=['Next_Id'], phrase='next')
        self.metamodel.define_relation('R1', endpint1, endpint2)
        
        first = self.metamodel.new('A', Name="First")
        second = self.metamodel.new('A', Name="Second")

        xtuml.model.relate(first, second, 1, 'prev')

        inst = xtuml.navigate_one(first).A[1, 'next']()
        self.assertEqual(inst.Name, second.Name)

        inst = xtuml.navigate_one(first).A[1, 'prev']()
        self.assertIsNone(inst)
        
        inst = xtuml.navigate_one(second).A[1, 'prev']()
        self.assertEqual(inst.Name, first.Name)
        
        inst = xtuml.navigate_one(second).A[1, 'next']()
        self.assertIsNone(inst)


    def testOneToMany(self):
        self.metamodel.define_class('A', [('Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id'), ('A_Id', 'unique_id')])
        a_endpint = xtuml.SingleAssociationLink('A')
        b_endpint = xtuml.ManyAssociationLink('B')
        
        self.metamodel.define_relation('R1', a_endpint, b_endpint)
        
        a = self.metamodel.new('A')
        b = self.metamodel.new('B')
        xtuml.relate(a, b, 1)
        
        self.assertEqual(a, xtuml.navigate_one(b).A[1]())
        


if __name__ == "__main__":
    unittest.main()

