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

    def test_filename_input(self):
        resources = os.path.dirname(__file__) + os.sep + 'resources'
        schema = resources + os.sep + 'ooaofooa_schema.sql'
        globs = resources + os.sep + 'Globals.xtuml'

        metamodel = xtuml.load_metamodel([globs, schema])
        self.assertTrue(metamodel.select_any('S_DT', xtuml.where_eq(Name='integer')) is not None)
        
    @load
    def test_table_named_create(self, m):
        '''
        CREATE TABLE CREATE (Id UNIQUE_ID);
        INSERT INTO CREATE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('CREATE') is not None)
        
    @load
    def test_table_named_table(self, m):
        '''
        CREATE TABLE TABLE (Id UNIQUE_ID);
        INSERT INTO TABLE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('TABLE') is not None)
        
    @load
    def test_table_named_insert(self, m):
        '''
        CREATE TABLE INSERT (Id UNIQUE_ID);
        INSERT INTO INSERT VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('INSERT') is not None)
        
    @load
    def test_table_named_into(self, m):
        '''
        CREATE TABLE INTO (Id UNIQUE_ID);
        INSERT INTO INTO VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('INTO') is not None)
        
    @load
    def test_table_named_values(self, m):
        '''
        CREATE TABLE VALUES (Id UNIQUE_ID);
        INSERT INTO VALUES VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('VALUES') is not None)
        
    @load
    def test_table_named_rop(self, m):
        '''
        CREATE TABLE ROP (Id UNIQUE_ID);
        INSERT INTO ROP VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('ROP') is not None)
        
    @load
    def test_table_named_ref_id(self, m):
        '''
        CREATE TABLE REF_ID (Id UNIQUE_ID);
        INSERT INTO REF_ID VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('REF_ID') is not None)
        
    @load
    def test_table_named_from(self, m):
        '''
        CREATE TABLE FROM (Id UNIQUE_ID);
        INSERT INTO FROM VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('FROM') is not None)
        
    @load
    def test_table_named_to(self, m):
        '''
        CREATE TABLE TO (Id UNIQUE_ID);
        INSERT INTO TO VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('TO') is not None)
        
    @load
    def test_table_named_phrase(self, m):
        '''
        CREATE TABLE PHRASE (Id UNIQUE_ID);
        INSERT INTO PHRASE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('PHRASE') is not None)
        
    @load
    def test_table_named_true(self, m):
        '''
        CREATE TABLE TRUE (Id UNIQUE_ID);
        INSERT INTO TRUE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('TRUE') is not None)
        
    @load
    def test_table_named_false(self, m):
        '''
        CREATE TABLE FALSE (Id UNIQUE_ID);
        INSERT INTO FALSE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('FALSE') is not None)
        
    @load
    def test_empty_attribute_sequence(self, m):
        '''
        CREATE TABLE X ();
        INSERT INTO X VALUES ();
        '''
        self.assertTrue(m.select_any('X') is not None)

    @load
    def test_insert_string(self, m):
        '''
        CREATE TABLE X (Id STRING);
        INSERT INTO X VALUES ('TEST');
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 'TEST')
        
    @load
    def test_insert_escaped_string(self, m):
        '''
        CREATE TABLE X (Id STRING);
        INSERT INTO X VALUES ('TE''ST');
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, "TE'ST")
        
    @load
    def test_insert_null_uuid(self, m):
        '''
        CREATE TABLE X (Id UNIQUE_ID);
        INSERT INTO X VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(0, val.Id)

    @load
    def test_insert_zero_uuid(self, m):
        '''
        CREATE TABLE X (Id UNIQUE_ID);
        INSERT INTO X VALUES (0);
        '''
        val = m.select_any('X')
        self.assertEqual(0, val.Id)
        
    @load
    def test_insert_positive_real(self, m):
        '''
        CREATE TABLE X (Id REAL);
        INSERT INTO X VALUES (1.1);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 1.1)
        
    @load
    def test_insert_negative_real(self, m):
        '''
        CREATE TABLE X (Id REAL);
        INSERT INTO X VALUES (-5.2);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, -5.2)

    @load
    def test_insert_positive_integer(self, m):
        '''
        CREATE TABLE X (Id INTEGER);
        INSERT INTO X VALUES (5);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 5)

    @load
    def test_insert_negative_integer(self, m):
        '''
        CREATE TABLE X (Id INTEGER);
        INSERT INTO X VALUES (-1000);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, -1000) 

    @load
    def test_insert_true(self, m):
        '''
        CREATE TABLE X (Id BOOLEAN);
        INSERT INTO X VALUES (true);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, True)
        
    @load
    def test_insert_false(self, m):
        '''
        CREATE TABLE X (Id BOOLEAN);
        INSERT INTO X VALUES (false);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, False)
        
    @load
    def test_rop_named_as_cardinality(self, m):
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
    def test_rop_without_identifier_sequence(self, m):
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
    def test_empty_input(self, m):
        ''''''
        pass
    
    @load
    def test_empty_input_with_comment(self, m):
        '''-- Some comment'''
        pass
        
    @expect_exception(xtuml.ParsingException)
    @load
    def test_illegal_character(self, m):
        '''
        CREATE TABLE & (Id INTEGER);
        '''

    @expect_exception(xtuml.ParsingException)
    @load
    def test_missing_semicolon(self, m):
        '''
        CREATE TABLE X (Id INTEGER)
        '''
        
    @expect_exception(xtuml.ParsingException)
    @load
    def test_invalid_token_sequence(self, m):
        '''
        TABLE CREATE X (Id INTEGER);
        '''
        self.assertTrue(False) # Should not execute
        
    @expect_exception(xtuml.ParsingException)
    @load
    def test_invalid_first_cardinality_number(self, m):
        '''
        CREATE ROP REF_ID R1 FROM 2 X ( Id )
                             TO   1 Y ( Id );
        '''
        self.assertTrue(False) # Should not execute
        
    @expect_exception(xtuml.ParsingException)
    @load
    def test_invalid_second_cardinality_number(self, m):
        '''
        CREATE ROP REF_ID R1 FROM 1 X ( Id )
                             TO   2 Y ( Id );
        '''
        self.assertTrue(False) # Should not execute
        
    @expect_exception(xtuml.ParsingException)
    @load
    def test_invalid_first_cardinality_letter(self, m):
        '''
        CREATE ROP REF_ID R1 FROM 1 X ( Id )
                             TO   X Y ( Id );
        '''
        self.assertTrue(False) # Should not execute
        
    @expect_exception(xtuml.ParsingException)
    @load
    def test_invalid_second_cardinality_letter(self, m):
        '''
        CREATE ROP REF_ID R1 FROM Y X ( Id )
                             TO   1 Y ( Id );
        '''
        self.assertTrue(False) # Should not execute
        
    @expect_exception(xtuml.ParsingException)
    @load
    def test_invalid_boolean_literal(self, m):
        '''
        CREATE TABLE X (B BOOLEAN);
        INSERT INTO X VALUES ('test');
        '''

    @expect_exception(xtuml.ParsingException)
    @load
    def test_invalid_type(self, m):
        '''
        CREATE TABLE X (VAR SOME_TYPE);
        INSERT INTO X VALUES ('test');
        '''

    @load
    def test_insert_with_undefined_table_and_argument(self, m):
        '''
        INSERT INTO X VALUES ('test');
        '''
        self.assertTrue(m.select_any('X'))
        
    @load
    def test_insert_with_undefined_table(self, m):
        '''
        INSERT INTO X VALUES ();
        '''
        self.assertTrue(m.select_any('X'))
    

if __name__ == "__main__":
    unittest.main()

