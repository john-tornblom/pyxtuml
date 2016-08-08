import os
import unittest
import xtuml
import bridgepoint

import bridgepoint.consistency_check


class TestConcistencyCLI(unittest.TestCase):
    '''
    Test suite for the bridgepoint.consistency_check 
    command line interface.
    '''
    def main(self, *args):
        try:
            return bridgepoint.consistency_check.main(list(args))
        except SystemExit as e:
            return e.code
    
    def test_no_args(self):
        rc = self.main()
        self.assertEqual(1, rc)
        
    def test_auto_include_globals(self):
        path = (os.path.dirname(__file__) + os.sep + os.pardir + os.sep + 
                'resources' + os.sep + 'Globals.xtuml')
                
        rc = self.main(path)
        self.assertEqual(0, rc)
        
        rc = self.main(path, '-g')
        self.assertNotEqual(0, rc)
        
    def test_limit_searchspace(self):
        path = (os.path.dirname(__file__) + os.sep + os.pardir + os.sep + 
                'resources' + os.sep + 'Globals.xtuml')

        rc = self.main(path, '-g')
        self.assertNotEqual(0, rc)
        
        rc = self.main(path, '-g', '-k', 'O_OBJ', '-r', '0')
        self.assertEqual(0, rc)
        
