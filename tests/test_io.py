# encoding: utf-8
# Copyright (C) 2014-2015 John Törnblom

import unittest
import os
import ply
import tempfile

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
        INSERT INTO X ('test');
        '''

    @expect_exception(xtuml.ParsingException)
    @load
    def testInvalidType(self, m):
        '''
        CREATE TABLE X (VAR SOME_TYPE);
        INSERT INTO X ('test');
        '''

    @expect_exception(xtuml.ParsingException)
    @load
    def testInsertWithUndefinedTableAndArgument(self, m):
        '''
        INSERT INTO X VALUES ('test');
        '''
    
    @expect_exception(xtuml.ParsingException)    
    @load
    def testInsertWithUndefinedTable(self, m):
        '''
        INSERT INTO X VALUES ();
        '''
        
    def testSurpressingUndefinedTable(self):
        self.loader.input('INSERT INTO X VALUES ();')
        self.loader.build_metamodel(ignore_undefined_classes=True)
        
    def testSurpressingUndefinedTableWithArgument(self):
        self.loader.input('INSERT INTO X VALUES (1);')
        self.loader.build_metamodel(ignore_undefined_classes=True)
    

class TestPersist(unittest.TestCase):
    '''
    Test suite for the module xtuml.persist
    '''

    def testSerialize(self):
        schema = '''
            CREATE TABLE X (BOOLEAN BOOLEAN,
                            INTEGER INTEGER,
                            REAL REAL,
                            STRING STRING,
                            UNIQUE_ID UNIQUE_ID);
        '''
        
        loader = xtuml.ModelLoader()
        loader.input(schema)
        
        m = loader.build_metamodel()
        m.new('X', BOOLEAN=True,
                   INTEGER=1,
                   REAL=-5.5,
                   UNIQUE_ID=1)
        
        s = xtuml.serialize_instances(m)
        
        loader = xtuml.ModelLoader()
        loader.input(schema)
        loader.input(s)
        
        m = loader.build_metamodel()
        x = m.select_any('X')
        self.assertEqual(x.BOOLEAN, True)
        self.assertEqual(x.INTEGER, 1)
        self.assertEqual(x.REAL, -5.5)
        self.assertEqual(x.UNIQUE_ID, 1)
        
        self.assertIsInstance(x.BOOLEAN, bool)
        self.assertIsInstance(x.INTEGER, int)
        self.assertIsInstance(x.REAL, float)
        
        # don't check type of unique_ids. they may differ.
        # python2 uses long, while python3 uses int.
        # besides, only equals comparisons operator (==) shall be used on these types.
        # self.assertIsInstance(x.UNIQUE_ID, int)
        
    def testSerializeDefaultValues(self):
        schema = '''
            CREATE TABLE X (BOOLEAN BOOLEAN,
                            INTEGER INTEGER,
                            REAL REAL,
                            STRING STRING,
                            UNIQUE_ID UNIQUE_ID);
        '''
        
        loader = xtuml.ModelLoader()
        loader.input(schema)

        id_generator = xtuml.IntegerGenerator()
        m = loader.build_metamodel(id_generator)
        m.new('X')
        
        s = xtuml.serialize_instances(m)
  
        loader = xtuml.ModelLoader()
        loader.input(schema)
        loader.input(s)

        id_generator = xtuml.IntegerGenerator()
        m = loader.build_metamodel(id_generator)
        x = m.select_any('X')
        self.assertEqual(x.BOOLEAN, False)
        self.assertEqual(x.INTEGER, 0)
        self.assertEqual(x.REAL, 0.0)
        self.assertEqual(x.UNIQUE_ID, 1)


    def testPersistDefaultValues(self):
        schema = '''
            CREATE TABLE X (BOOLEAN BOOLEAN,
                            INTEGER INTEGER,
                            REAL REAL,
                            STRING STRING,
                            UNIQUE_ID UNIQUE_ID);
        '''
        
        loader = xtuml.ModelLoader()
        loader.input(schema)
        
        id_generator = xtuml.IntegerGenerator()
        m = loader.build_metamodel(id_generator)
        m.new('X')
        
        s = xtuml.serialize_instances(m)
        
        (_, filename) = tempfile.mkstemp()
        try:
            xtuml.persist_instances(m, filename)
            with open(filename) as f:
                self.assertEqual(s, f.read())
        finally:
            os.remove(filename)
        
        loader = xtuml.ModelLoader()
        loader.input(schema)
        loader.input(s)

        id_generator = xtuml.IntegerGenerator()
        m = loader.build_metamodel(id_generator)
        x = m.select_any('X')
        self.assertEqual(x.BOOLEAN, False)
        self.assertEqual(x.INTEGER, 0)
        self.assertEqual(x.REAL, 0.0)
        self.assertEqual(x.UNIQUE_ID, 1)

    def testPersistSchema(self):
        schema = '''
            CREATE TABLE X (BOOLEAN BOOLEAN,
                            INTEGER INTEGER,
                            REAL REAL,
                            STRING STRING,
                            UNIQUE_ID UNIQUE_ID,
                            Next UNIQUE_ID);
                            
        CREATE ROP REF_ID R1 FROM 1C X ( UNIQUE_ID ) PHRASE 'precedes'
                             TO   1C X ( Next ) PHRASE 'succeeds';
        '''
        loader = xtuml.ModelLoader()
        loader.input(schema)
        m = loader.build_metamodel()
        s = xtuml.serialize_schema(m)
    
        (_, filename) = tempfile.mkstemp()
        try:
            xtuml.persist_schema(m, filename)
            with open(filename) as f:
                self.assertEqual(s, f.read())
        finally:
            os.remove(filename)

    def testPersistDatabase(self):
        schema = '''
            CREATE TABLE X (BOOLEAN BOOLEAN,
                            INTEGER INTEGER,
                            REAL REAL,
                            STRING STRING,
                            UNIQUE_ID UNIQUE_ID,
                            Next UNIQUE_ID);
                            
        CREATE ROP REF_ID R1 FROM 1C X ( Next ) PHRASE 'precedes'
                             TO   1C X ( UNIQUE_ID ) PHRASE 'succeeds';
        '''
        loader = xtuml.ModelLoader()
        loader.input(schema)
        m = loader.build_metamodel()
        m.new('X', Boolean=True, Integer=4, String='str', Uniquie_Id=5)
        
        s = xtuml.serialize_database(m)
    
        (_, filename) = tempfile.mkstemp()
        try:
            xtuml.persist_database(m, filename)
            with open(filename) as f:
                self.assertEqual(s, f.read())
        finally:
            os.remove(filename)

    def testSerializeSchema(self):
        schema = '''
            CREATE TABLE X (BOOLEAN BOOLEAN,
                            INTEGER INTEGER,
                            REAL REAL,
                            STRING STRING,
                            UNIQUE_ID UNIQUE_ID,
                            Next UNIQUE_ID);
                            
        CREATE ROP REF_ID R1 FROM 1C X ( Next ) PHRASE 'precedes'
                             TO   1C X ( UNIQUE_ID ) PHRASE 'succeeds';
        '''
        loader = xtuml.ModelLoader()
        loader.input(schema)
        m = loader.build_metamodel()
        x1 = m.new('X', Boolean=True, Integer=4, String='str')
        x2 = m.new('X', Boolean=True, Integer=4, String='str')
        xtuml.relate(x1, x2, 1, 'precedes')
        
        s = xtuml.serialize_schema(m)
        loader = xtuml.ModelLoader()
        loader.input(s)
        m = loader.build_metamodel()

        self.assertFalse(m.select_any('X'))

        x1 = m.new('X', Boolean=True, Integer=4, String='str')
        x2 = m.new('X', Boolean=True, Integer=4, String='str')
        xtuml.relate(x1, x2, 1, 'succeeds')

        self.assertTrue(xtuml.navigate_one(x1).X[1, 'precedes']())
        
    def testSerializeNoneValues(self):
        schema = '''
            CREATE TABLE X (BOOLEAN BOOLEAN,
                            INTEGER INTEGER,
                            REAL REAL,
                            STRING STRING,
                            UNIQUE_ID UNIQUE_ID);
        '''
        loader = xtuml.ModelLoader()
        loader.input(schema)

        id_generator = xtuml.IntegerGenerator()
        m = loader.build_metamodel(id_generator)
        x = m.new('X')
        x.boolean = None
        x.Integer = None
        x.ReaL = None
        x.UNIQUE_ID = None
        s = xtuml.serialize_instances(m)

        loader = xtuml.ModelLoader()
        loader.input(schema)
        loader.input(s)

        id_generator = xtuml.IntegerGenerator()
        m = loader.build_metamodel(id_generator)
        x = m.select_any('X')
        self.assertEqual(x.BOOLEAN, False)
        self.assertEqual(x.INTEGER, 0)
        self.assertEqual(x.REAL, 0.0)
        self.assertEqual(x.UNIQUE_ID, 0)

    def testSerializeAttributeNamedSelf(self):
        schema = '''
            CREATE TABLE X (self UNIQUE_ID);
        '''
        
        loader = xtuml.ModelLoader()
        loader.input(schema)
        
        m = loader.build_metamodel()
        m.new('X', 1)
        
        s = xtuml.serialize_instances(m)
        
        loader = xtuml.ModelLoader()
        loader.input(schema)
        loader.input(s)
        
        m = loader.build_metamodel()
        x = m.select_any('X')
        self.assertEqual(x.self, 1)

    
def compare_metamodel_classes(m1, m2):
    '''
    Helper function for detecting differences in class definitions 
    in two metamodels.
    '''
    if len(m1.classes.keys()) != len(m2.classes.keys()):
        return False
    
    for kind in m1.classes.keys():
        Cls1 = m1.classes[kind]
        Cls2 = m2.classes[kind]
        
        if Cls1.__name__ != Cls2.__name__:
            return False
        
        if Cls1.__a__ != Cls2.__a__:
            return False

        if Cls1.__i__ != Cls2.__i__:
            return False

        if Cls1.__d__ != Cls2.__d__:
            return False
        
    return True


def schema_compare(fn):
    '''
    Decorator for testing schema serialization capabilities 
    from stimuli defined as doc-strings on unit tests.
    '''
    def compare_wrapper(self, *args, **kwargs):
        loader = xtuml.ModelLoader()
        loader.input(fn.__doc__)
        m1 = loader.build_metamodel()
        
        s = xtuml.serialize_schema(m1)

        loader = xtuml.ModelLoader()
        loader.input(s)
        m2 = loader.build_metamodel()
        
        self.assertTrue(compare_metamodel_classes(m1, m2))
        fn(self)
    
    return compare_wrapper


class TestSchema(unittest.TestCase):
    '''
    Test suite for schema serialization capabilities in 
    the module xtuml.persist
    '''
    
    @schema_compare
    def testClassWithDataTypeNames(self):
        '''
            CREATE TABLE X (BOOLEAN BOOLEAN,
                            INTEGER INTEGER,
                            REAL REAL,
                            STRING STRING,
                            UNIQUE_ID UNIQUE_ID);
        '''
        
    @schema_compare
    def testROPNamedAsCardinality(self):
        '''
        CREATE TABLE M  (Id INTEGER, MC_Id INTEGER);
        CREATE TABLE MC (Id INTEGER);
        
        CREATE ROP REF_ID R1 FROM M M ( MC_Id )
                             TO   1 MC ( Id );
        '''

    @schema_compare
    def testROPWithoutIdentifiers(self):
        '''
        CREATE TABLE X ();
        CREATE TABLE Y ();
        
        CREATE ROP REF_ID R1 FROM MC X ()
                             TO   MC Y ();
        '''

if __name__ == "__main__":
    unittest.main()

