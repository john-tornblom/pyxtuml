# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import unittest

import xtuml.rsl.symtab

class TestSymbolTable(unittest.TestCase):


    def testSymbolStore(self):
        symtab = xtuml.rsl.symtab.SymbolTable()
        handle = "TEST"
        
        symtab.enter_scope()
        symtab.enter_scope()
        
        symtab.install_symbol('Test', handle)
        value = symtab.find_symbol("Test")
        symtab.leave_scope()
        
        self.assertRaises(xtuml.rsl.symtab.SymtabException, symtab.find_symbol, "Test")
        
        self.assertEqual(handle, value)
        
        
    def testGlobalStore(self):
        symtab = xtuml.rsl.symtab.SymbolTable()

        g1 = "Test1"
        g2 = "Test2"
        
        symtab.enter_scope()
        symtab.install_global("g1", g1)
        
        symtab.enter_scope()
        symtab.install_global("g2", g2)
        symtab.leave_scope()

        self.assertEqual(symtab.find_symbol("g1"), g1)
        self.assertEqual(symtab.find_symbol("g2"), g2)
        
        symtab.leave_scope()
        
        self.assertRaises(xtuml.rsl.symtab.SymtabException, symtab.find_symbol, "g1")
        self.assertRaises(xtuml.rsl.symtab.SymtabException, symtab.find_symbol, "g2")
        
    def testOutOfScope(self):
        symtab = xtuml.rsl.symtab.SymbolTable()
        self.assertRaises(xtuml.rsl.symtab.SymtabException, symtab.leave_scope)

    def testOutOfBlock(self):
        symtab = xtuml.rsl.symtab.SymbolTable()
        
        symtab.enter_scope()
        symtab.leave_block()
        
        self.assertRaises(xtuml.rsl.symtab.SymtabException, symtab.leave_block)
        
    def testSymbolRewrite(self):
        symtab = xtuml.rsl.symtab.SymbolTable()
        
        symtab.enter_scope()
        
        symtab.install_symbol('TEST', 'TEST1')
        symtab.install_symbol('TEST', 'TEST2')
        
        value = symtab.find_symbol("TEST")
        symtab.leave_scope()
        
        self.assertEqual(value, 'TEST2')
        
    def testGetScopeSymbols(self):
        symtab = xtuml.rsl.symtab.SymbolTable()
        
        symtab.enter_scope()
        self.assertEqual(len(symtab.scope_head.symbols), 0)
        
        symtab.install_symbol('TEST', 'TEST1')
        symtab.install_symbol('TEST', 'TEST2')
        self.assertEqual(len(symtab.scope_head.symbols), 1)
        
        symtab.install_symbol('TEST1', '')
        self.assertEqual(len(symtab.scope_head.symbols), 2)

        symtab.leave_scope()
        
        symtab.enter_scope()
        self.assertEqual(len(symtab.scope_head.symbols), 0)
        
