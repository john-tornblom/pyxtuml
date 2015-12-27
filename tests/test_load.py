# encoding: utf-8
# Copyright (C) 2014-2015 John Törnblom

import unittest
import os

import xtuml

from tests.utils import expect_exception


def load(fn):
    '''
    Decorator for loading a meta model from a test case doc string
    '''
    def load_wrapper(self, *args, **kwargs):
        self.loader.input(fn.__doc__)
        metamodel = self.loader.build_metamodel()
        fn(self, metamodel)
    
    return load_wrapper


class TestLoader(unittest.TestCase):
    '''
    Test suite for the class  xtuml.ModelLoader
    '''
    
    def setUp(self):
        self.loader = xtuml.ModelLoader()

    def tearDown(self):
        del self.loader

    def testFilenameInput(self):
        resources = os.path.dirname(__file__) + os.sep + 'resources'
        schema = resources + os.sep + 'ooaofooa_schema.sql'
        globs = resources + os.sep + 'Globals.xtuml'

        metamodel = xtuml.load_metamodel([globs, schema])
        self.assertTrue(metamodel.select_any('S_DT', xtuml.where_eq(Name='integer')) is not None)
        
    @load
    def testTableNamedCREATE(self, m):
        '''
        CREATE TABLE CREATE (Id UNIQUE_ID);
        INSERT INTO CREATE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('CREATE') is not None)
        
    @load
    def testTableNamedTABLE(self, m):
        '''
        CREATE TABLE TABLE (Id UNIQUE_ID);
        INSERT INTO TABLE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('TABLE') is not None)
        
    @load
    def testTableNamedINSERT(self, m):
        '''
        CREATE TABLE INSERT (Id UNIQUE_ID);
        INSERT INTO INSERT VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('INSERT') is not None)
        
    @load
    def testTableNamedINTO(self, m):
        '''
        CREATE TABLE INTO (Id UNIQUE_ID);
        INSERT INTO INTO VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('INTO') is not None)
        
    @load
    def testTableNamedVALUES(self, m):
        '''
        CREATE TABLE VALUES (Id UNIQUE_ID);
        INSERT INTO VALUES VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('VALUES') is not None)
        
    @load
    def testTableNamedROP(self, m):
        '''
        CREATE TABLE ROP (Id UNIQUE_ID);
        INSERT INTO ROP VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('ROP') is not None)
        
    @load
    def testTableNamedREF_ID(self, m):
        '''
        CREATE TABLE REF_ID (Id UNIQUE_ID);
        INSERT INTO REF_ID VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('REF_ID') is not None)
        
    @load
    def testTableNamedFROM(self, m):
        '''
        CREATE TABLE FROM (Id UNIQUE_ID);
        INSERT INTO FROM VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('FROM') is not None)
        
    @load
    def testTableNamedTO(self, m):
        '''
        CREATE TABLE TO (Id UNIQUE_ID);
        INSERT INTO TO VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('TO') is not None)
        
    @load
    def testTableNamedPHRASE(self, m):
        '''
        CREATE TABLE PHRASE (Id UNIQUE_ID);
        INSERT INTO PHRASE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('PHRASE') is not None)
        
    @load
    def testTableNamedTRUE(self, m):
        '''
        CREATE TABLE TRUE (Id UNIQUE_ID);
        INSERT INTO TRUE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('TRUE') is not None)
        
    @load
    def testTableNamedFALSE(self, m):
        '''
        CREATE TABLE FALSE (Id UNIQUE_ID);
        INSERT INTO FALSE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('FALSE') is not None)
        
    @load
    def testEmptyAttributeList(self, m):
        '''
        CREATE TABLE X ();
        INSERT INTO X VALUES ();
        '''
        self.assertTrue(m.select_any('X') is not None)

    @load
    def testInsertSTRING(self, m):
        '''
        CREATE TABLE X (Id STRING);
        INSERT INTO X VALUES ('TEST');
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 'TEST')
        
    @load
    def testInsertEscapedSTRING(self, m):
        '''
        CREATE TABLE X (Id STRING);
        INSERT INTO X VALUES ('TE''ST');
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, "TE'ST")
        
    @load
    def testInsertUNIQUE_ID_Null(self, m):
        '''
        CREATE TABLE X (Id UNIQUE_ID);
        INSERT INTO X VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(0, val.Id)

    @load
    def testInsertUNIQUE_ID_Zero(self, m):
        '''
        CREATE TABLE X (Id UNIQUE_ID);
        INSERT INTO X VALUES (0);
        '''
        val = m.select_any('X')
        self.assertEqual(0, val.Id)
        
    @load
    def testInsertREAL_Positive(self, m):
        '''
        CREATE TABLE X (Id REAL);
        INSERT INTO X VALUES (1.1);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 1.1)
        
    @load
    def testInsertREAL_Negative(self, m):
        '''
        CREATE TABLE X (Id REAL);
        INSERT INTO X VALUES (-5.2);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, -5.2)

    @load
    def testInsertINTEGER_Positive(self, m):
        '''
        CREATE TABLE X (Id INTEGER);
        INSERT INTO X VALUES (5);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 5)
        
    @load
    def testInsertBOOLEAN_True(self, m):
        '''
        CREATE TABLE X (Id BOOLEAN);
        INSERT INTO X VALUES (true);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, True)
        
    @load
    def testInsertBOOLEAN_False(self, m):
        '''
        CREATE TABLE X (Id BOOLEAN);
        INSERT INTO X VALUES (false);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, False)
        
    @load
    def testInsertINTEGER_Negative(self, m):
        '''
        CREATE TABLE X (Id INTEGER);
        INSERT INTO X VALUES (-1000);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, -1000) 

    @load
    def testROPNamedAsCardinality(self, m):
        '''
        CREATE TABLE M  (Id INTEGER, MC_Id INTEGER);
        CREATE TABLE MC (Id INTEGER);
        
        CREATE ROP REF_ID R1 FROM M M ( MC_Id )
                             TO   1 MC ( Id );
                             
        INSERT INTO MC VALUES (2);
        INSERT INTO M  VALUES (1, 2);
        '''
        val = m.select_any('M')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 1) 
        
        val = xtuml.navigate_one(val).MC[1]()
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 2) 

    @load
    def testROPWithoutIdentifiers(self, m):
        '''
        CREATE TABLE X  ();
        CREATE TABLE Y ();
        
        CREATE ROP REF_ID R1 FROM MC X ()
                             TO   MC Y ();
                             
        INSERT INTO X VALUES ();
        INSERT INTO Y VALUES ();
        '''
        x = m.select_any('X')
        self.assertTrue(x is not None)

        y = xtuml.navigate_one(x).Y[1]()
        self.assertTrue(y is not None)

    @load
    def testEmptyInput(self, m):
        ''''''
        pass
    
    @load
    def testEmptyInputWithComment(self, m):
        '''-- Some comment'''
        pass
        
    @expect_exception(xtuml.ParsingException)
    @load
    def testIllegalCharacter(self, m):
        '''
        CREATE TABLE & (Id INTEGER);
        '''

    @expect_exception(xtuml.ParsingException)
    @load
    def testMissingSemiColon(self, m):
        '''
        CREATE TABLE X (Id INTEGER)
        '''
        
    @expect_exception(xtuml.ParsingException)
    @load
    def testInvalidTokenSequence(self, m):
        '''
        TABLE CREATE X (Id INTEGER);
        '''
        self.assertTrue(False) # Should not execute
        
    @expect_exception(xtuml.ParsingException)
    @load
    def testInvalidFirstCardinalityNumber(self, m):
        '''
        CREATE ROP REF_ID R1 FROM 2 X ( Id )
                             TO   1 Y ( Id );
        '''
        self.assertTrue(False) # Should not execute
        
    @expect_exception(xtuml.ParsingException)
    @load
    def testInvalidSecondCardinalityNumber(self, m):
        '''
        CREATE ROP REF_ID R1 FROM 1 X ( Id )
                             TO   2 Y ( Id );
        '''
        self.assertTrue(False) # Should not execute
        
    @expect_exception(xtuml.ParsingException)
    @load
    def testInvalidFirstCardinalityLetter(self, m):
        '''
        CREATE ROP REF_ID R1 FROM 1 X ( Id )
                             TO   X Y ( Id );
        '''
        self.assertTrue(False) # Should not execute
        
    @expect_exception(xtuml.ParsingException)
    @load
    def testInvalidSecondCardinalityLetter(self, m):
        '''
        CREATE ROP REF_ID R1 FROM Y X ( Id )
                             TO   1 Y ( Id );
        '''
        self.assertTrue(False) # Should not execute
        
    @expect_exception(xtuml.ParsingException)
    @load
    def testInvalidBooleanLiteral(self, m):
        '''
        CREATE TABLE X (B BOOLEAN);
        INSERT INTO X VALUES ('test');
        '''

    @expect_exception(xtuml.ParsingException)
    @load
    def testInvalidType(self, m):
        '''
        CREATE TABLE X (VAR SOME_TYPE);
        INSERT INTO X VALUES ('test');
        '''

    @load
    def testInsertWithUndefinedTableAndArgument(self, m):
        '''
        INSERT INTO X VALUES ('test');
        '''
        self.assertTrue(m.select_any('X'))
        
    @load
    def testInsertWithUndefinedTable(self, m):
        '''
        INSERT INTO X VALUES ();
        '''
        self.assertTrue(m.select_any('X'))
    

if __name__ == "__main__":
    unittest.main()

