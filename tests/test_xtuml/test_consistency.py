import unittest
import xtuml
import bridgepoint

class TestConcistency(unittest.TestCase):
    '''
    Test suite for the module xtuml.consistency_check
    '''
 
    def setUp(self):
        self.metamodel = bridgepoint.load_metamodel()

    def tearDown(self):
        del self.metamodel
        
    def test_empty_model(self):
        self.assertTrue(self.metamodel.is_consistent())
    
    def test_association_integrity(self):
        m = self.metamodel
        s_dt = m.select_one('S_DT', xtuml.where_eq(Name='string'))
        s_bparm = m.new('S_BPARM', Name='My_Parameter')
        s_ee = m.new('S_EE', Name='My_External_Entity', Key_Lett='My_External_Entity')
        pe_pe = m.new('PE_PE', Visibility=True, type=5)
        s_brg = m.new('S_BRG', Name='My_Bridge_Operation')
        
        
        self.assertFalse(xtuml.check_association_integrity(m, 22))
        self.assertTrue(xtuml.relate(s_bparm, s_dt, 22))
        self.assertTrue(xtuml.check_association_integrity(m, 22))
        
        self.assertFalse(xtuml.check_association_integrity(m, 21))
        self.assertTrue(xtuml.relate(s_bparm, s_brg, 21))
        self.assertTrue(xtuml.check_association_integrity(m, 21))
        
        self.assertFalse(xtuml.check_association_integrity(m, 20))
        self.assertTrue(xtuml.relate(s_brg, s_dt, 20))
        self.assertTrue(xtuml.check_association_integrity(m, 20))
        
        self.assertFalse(xtuml.check_association_integrity(m, 8001))
        self.assertTrue(xtuml.relate(s_ee, pe_pe, 8001))
        self.assertTrue(xtuml.check_association_integrity(m, 8001))
        
        self.assertFalse(xtuml.check_association_integrity(m, 19))
        self.assertTrue(xtuml.relate(s_brg, s_ee, 19))
        self.assertTrue(xtuml.check_association_integrity(m, 19))
        
        # the old, unused association R8 is still present in ooaofooa, and thus
        # consistency check fails on S_EE.
        #self.assertTrue(m.is_consistent())
        
    def test_uniqueness_constraint(self):
        m = self.metamodel
        self.assertTrue(m.is_consistent())
        
        s_dt = m.select_one('S_DT', xtuml.where_eq(Name='string'))
        m.clone(s_dt)
        
        self.assertFalse(m.is_consistent())
        self.assertTrue(xtuml.check_uniqueness_constraint(m, 'PE_PE'))
        
        xtuml.delete(s_dt)
        self.assertTrue(m.is_consistent())
