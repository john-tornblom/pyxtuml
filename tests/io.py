# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import unittest
import os

from xtuml import model
from xtuml import io


def load(fn):
    def load_wrapper(self, *args, **kwargs):
        self.loader.input(fn.__doc__)
        id_generator = model.IdGenerator()
        metamodel = self.loader.build_metamodel(id_generator)
        fn(self, metamodel)
    
    return load_wrapper


class TestLoader(unittest.TestCase):

    def setUp(self):
        self.loader = io.load.ModelLoader()
        self.loader.build_parser()

    def tearDown(self):
        del self.loader

    def testFileInput(self):
        base_dir = '%s/../resources' % os.path.dirname(__file__)
        self.loader.filename_input('%s/ooaofooa_schema.sql' % base_dir)
        self.loader.filename_input('%s/Globals.xtuml' % base_dir)

        id_generator = model.IdGenerator()
        metamodel = self.loader.build_metamodel(id_generator)
        self.assertTrue(metamodel.select_any('S_DT', Name='integer') is not None)
        
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
    def testEmptyAttributeList(self, m):
        '''
        CREATE TABLE X ();
        INSERT INTO X VALUES ();
        '''
        self.assertTrue(m.select_any('X') is not None)


def suite():
    loader = unittest.TestLoader()
    s = loader.loadTestsFromTestCase(TestLoader)
    
    return s

