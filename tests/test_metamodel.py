# encoding: utf-8
# Copyright (C) 2014-2015 John Törnblom

import unittest

import xtuml
from bridgepoint import ooaofooa

def expect_exception(exception):
    def test_decorator(fn):
        def test_decorated(self, *args, **kwargs):
            self.assertRaises(exception, fn, self, *args, **kwargs)
        return test_decorated
    return test_decorator


class TestNavChain(unittest.TestCase):
    
    def testNavigateNone(self):
        self.assertIsNone(xtuml.navigate_one(None)())
        self.assertEqual(len(xtuml.navigate_many(None)()), 0)

    @expect_exception(xtuml.ModelException)
    def testNavigateInvalidHandle(self):
        self.assertIsNone(xtuml.navigate_one('test')())

        
class TestModel(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.loader = ooaofooa.Loader()
 
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
        pe_pe = self.metamodel.new('PE_PE')
        self.assertTrue(xtuml.relate(s_dt, pe_pe, 8001))
        self.assertTrue(xtuml.relate(s_dt, s_edt, 17))
        self.assertEqual(s_edt, xtuml.navigate_one(s_dt).S_EDT[17]())

    def testRelateReflexive1(self):
        inst1 = self.metamodel.new('ACT_SMT')
        inst2 = self.metamodel.new('ACT_SMT')
        act_blk = self.metamodel.new('ACT_BLK')

        self.assertTrue(xtuml.relate(inst1, act_blk, 602))
        self.assertTrue(xtuml.relate(inst2, act_blk, 602))
        self.assertTrue(xtuml.relate(inst1, inst2, 661, 'precedes'))
        self.assertEqual(inst2, xtuml.navigate_one(inst1).ACT_SMT[661, 'succeeds']())
        self.assertEqual(inst1, xtuml.navigate_one(inst2).ACT_SMT[661, 'precedes']())
        
    def testRelateReflexive2(self):
        inst1 = self.metamodel.new('ACT_SMT')
        inst2 = self.metamodel.new('ACT_SMT')
        act_blk = self.metamodel.new('ACT_BLK')

        self.assertTrue(xtuml.relate(inst1, act_blk, 602))
        self.assertTrue(xtuml.relate(inst2, act_blk, 602))
        self.assertTrue(xtuml.relate(inst2, inst1, 661, 'succeeds'))
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
        pe_pe = self.metamodel.new('PE_PE')
        self.assertTrue(xtuml.relate(pe_pe, s_dt, 8001))
        self.assertTrue(xtuml.relate(s_edt, s_dt, 17))
        self.assertEqual(s_edt, xtuml.navigate_one(s_dt).S_EDT[17]())
    
    @expect_exception(xtuml.ModelException)
    def testRelateInvalidRelId(self):
        s_edt = self.metamodel.new('S_EDT')
        s_dt = self.metamodel.new('S_DT')
        xtuml.relate(s_edt, s_dt, 0)
        self.assertEqual(s_edt, xtuml.navigate_one(s_dt).S_EDT[17]())
        
    def testUnrelate(self):
        inst1 = self.metamodel.new('ACT_SMT')
        inst2 = self.metamodel.new('ACT_SMT')
        act_blk = self.metamodel.new('ACT_BLK')

        self.assertTrue(xtuml.relate(inst1, act_blk, 602))
        self.assertTrue(xtuml.relate(inst2, act_blk, 602))
        
        self.assertTrue(xtuml.relate(inst1, inst2, 661, 'precedes'))
        self.assertEqual(inst2, xtuml.navigate_one(inst1).ACT_SMT[661, 'succeeds']())
        self.assertEqual(inst1, xtuml.navigate_one(inst2).ACT_SMT[661, 'precedes']())
        
        self.assertTrue(xtuml.unrelate(inst1, inst2, 661, 'precedes'))
        self.assertIsNone(xtuml.navigate_one(inst2).ACT_SMT[661, 'precedes']())
        self.assertIsNone(xtuml.navigate_one(inst1).ACT_SMT[661, 'succeeds']())
            
    def testRelateInWrongOrder(self):
        s_ee = self.metamodel.new('S_EE')
        pe_pe = self.metamodel.new('PE_PE')
        EE_ID = s_ee.EE_ID
        Element_ID = pe_pe.Element_ID
        self.assertTrue(xtuml.relate(s_ee, pe_pe, 8001))
        self.assertNotEqual(EE_ID, s_ee.EE_ID)
        self.assertEqual(Element_ID, pe_pe.Element_ID)

    def testRelateTopDown(self):
        m = self.metamodel
        s_dt = m.select_one('S_DT', lambda selected: selected.Name == 'string')
        s_bparm = m.new('S_BPARM', Name='My_Parameter')
        s_ee = m.new('S_EE', Name='My_External_Entity', Key_Lett='My_External_Entity')
        pe_pe = m.new('PE_PE', Visibility=True, type=5)
        s_brg = m.new('S_BRG', Name='My_Bridge_Operation')

        self.assertTrue(xtuml.relate(s_ee, pe_pe, 8001))
        self.assertTrue(xtuml.relate(s_brg, s_ee, 19))
        self.assertTrue(xtuml.relate(s_brg, s_dt, 20))
        self.assertTrue(xtuml.relate(s_bparm, s_brg, 21))
        self.assertTrue(xtuml.relate(s_bparm, s_dt, 22))
            
        inst = xtuml.navigate_any(pe_pe).S_EE[8001].S_BRG[19].S_BPARM[21]()
        self.assertEqual(inst, s_bparm)
        
    def testRelateBottomUp(self):
        m = self.metamodel
        s_dt = m.select_one('S_DT', lambda selected: selected.Name == 'string')
        s_bparm = m.new('S_BPARM', Name='My_Parameter')
        s_ee = m.new('S_EE', Name='My_External_Entity', Key_Lett='My_External_Entity')
        pe_pe = m.new('PE_PE', Visibility=True, type=5)
        s_brg = m.new('S_BRG', Name='My_Bridge_Operation')
        
        self.assertTrue(xtuml.relate(s_bparm, s_dt, 22))
        self.assertTrue(xtuml.relate(s_bparm, s_brg, 21))
        self.assertTrue(xtuml.relate(s_brg, s_dt, 20))
        self.assertTrue(xtuml.relate(s_ee, pe_pe, 8001))
        self.assertTrue(xtuml.relate(s_brg, s_ee, 19))
        
            
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

        self.assertTrue(xtuml.model.relate(first, second, 1, 'prev'))

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
        a_endpint = xtuml.SingleAssociationLink('A', ids=['Id'])
        b_endpint = xtuml.ManyAssociationLink('B', ids=['A_Id'])
        
        self.metamodel.define_relation(1, a_endpint, b_endpint)
        
        a = self.metamodel.new('A')
        b = self.metamodel.new('B')
        self.assertTrue(xtuml.relate(a, b, 1))
        
        self.assertEqual(a, xtuml.navigate_one(b).A[1]())

    def testCaseSensitivity(self):
        self.metamodel.define_class('Aa', [])
        
        self.metamodel.new('AA')

        self.assertTrue(self.metamodel.select_any('aA'))
        self.assertTrue(self.metamodel.select_any('AA'))
        self.assertTrue(self.metamodel.select_any('Aa'))
        self.assertTrue(self.metamodel.select_any('aa'))

        self.metamodel.new('Aa')
        self.metamodel.new('aA')
        self.metamodel.new('aa')
        
        self.assertEqual(len(self.metamodel.select_many('aA')), 4)
        self.assertEqual(len(self.metamodel.select_many('AA')), 4)
        self.assertEqual(len(self.metamodel.select_many('Aa')), 4)
        self.assertEqual(len(self.metamodel.select_many('aa')), 4)
        

    @expect_exception(xtuml.ModelException)
    def testUnknownType(self):
        self.metamodel.define_class('A', [('Id', '<invalid type>')])
        self.metamodel.new('A')


class TestBaseObject(unittest.TestCase):
 
    def testPlusOperator(self):
        inst1 = xtuml.BaseObject()
        inst2 = xtuml.BaseObject()

        q = inst1 + inst2
        self.assertEqual(2, len(q))
        self.assertIn(inst1, q)
        self.assertIn(inst2, q)
        
    def testMinusOperator(self):
        inst1 = xtuml.BaseObject()
        inst2 = xtuml.BaseObject()

        q = inst1 - inst2
        self.assertEqual(1, len(q))
        self.assertIn(inst1, q)
        self.assertNotIn(inst2, q)
        
    def testNonPersistingAttribute(self):
        inst = xtuml.BaseObject()
        
        setattr(inst, 'test1', 1)
        self.assertEqual(getattr(inst, 'test1'), 1)
        self.assertEqual(inst.test1, 1)
        
        inst.__dict__['test2'] = 2
        self.assertEqual(getattr(inst, 'test2'), 2)
        self.assertEqual(inst.test2, 2)

        inst.test3 = 3
        self.assertEqual(getattr(inst, 'test3'), 3)
        self.assertEqual(inst.test3, 3)
        
    @expect_exception(AttributeError)
    def testUndefinedAttribute1(self):
        inst = xtuml.BaseObject()
        _ = getattr(inst, 'test')
        
        
    @expect_exception(AttributeError)
    def testUndefinedAttribute2(self):
        inst = xtuml.BaseObject()
        _ = inst.test
        
        
class TestQuerySet(unittest.TestCase):
 
    def testEqualOperator(self):
        q1 = xtuml.QuerySet()
        q2 = xtuml.QuerySet()
        
        self.assertEqual(q1, q2)
        
        q1 = xtuml.QuerySet([1])
        q2 = xtuml.QuerySet([1])
        
        self.assertEqual(q1, q2)
        
        q1 = xtuml.QuerySet([1, 2, 3])
        q2 = xtuml.QuerySet([1, 2, 3])
        
        self.assertEqual(q1, q2)
        self.assertEqual(q1, [1, 2, 3])
        
    def testNotEqualOperator(self):
        q1 = xtuml.QuerySet()
        q2 = xtuml.QuerySet([1])
        self.assertNotEqual(q1, q2)
        self.assertNotEqual(q2, q1)
        
        q1 = xtuml.QuerySet([1, 2, 3])
        q2 = xtuml.QuerySet([1, 3])
        self.assertNotEqual(q1, q2)
        self.assertNotEqual(q2, q1)
        
        q1 = xtuml.QuerySet([1, 2, 3])
        q2 = xtuml.QuerySet([1, 3, 2])
        self.assertNotEqual(q1, q2)
        
    @expect_exception(KeyError)
    def testPopEmpty(self):
        q = xtuml.QuerySet()
        q.pop()
        

    def testPopLast(self):
        q1 = xtuml.QuerySet([1, 2])
        q2 = xtuml.QuerySet([1])
        self.assertNotEqual(q1, q2)

        q1.pop()
        self.assertEqual(q1, q2)
        
        
    def testPopFirst(self):
        q1 = xtuml.QuerySet([2, 1])
        q2 = xtuml.QuerySet([1])
        self.assertNotEqual(q1, q2)

        q1.pop(last=False)
        self.assertEqual(q1, q2)
        
if __name__ == "__main__":
    unittest.main()

