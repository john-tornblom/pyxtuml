# encoding: utf-8
# Copyright (C) 2014 John Törnblom
'''
Symbol table for the rule-specification language (RSL).  
'''


class SymtabException(Exception):
    pass


class Block(dict):
    pass


class Scope(list):
    
    def __init__(self):
        self.append(Block())

    @property
    def symbols(self):
        return_symbols = dict()
        for d in self:
            return_symbols.update(d)
            
        return return_symbols.items()
    

class SymbolTable(object):

    def __init__(self):
        self._global_scope = dict()
        self._functions = dict()
        self._scopes = list()
        
    @property
    def scope_head(self):
        if not len(self._scopes): 
            raise SymtabException('Out of scope')
        
        return self._scopes[-1]
    
    def enter_scope(self):
        scope = Scope()
        self._scopes.append(scope)

    def leave_scope(self):
        if not len(self._scopes): 
            raise SymtabException('Out of scope')
        
        d = dict()
        for block in self._scopes.pop():
            d.update(block)
        return d
    
    def enter_block(self):        
        block = Block()
        self.scope_head.append(block)
    
    def leave_block(self):
        if not len(self.scope_head): 
            raise SymtabException('Out of block')
        
        block = self.scope_head.pop()
        del block
    
    def install_global(self, name, handle):
        self._global_scope[name] = handle
        
    def install_symbol(self, name, handle):
        for block in self.scope_head:
            for key in block.keys():
                if key.lower() == name.lower():
                    block[key] = handle
                    return

        block = self.scope_head[-1]
        block[name] = handle

    def find_symbol(self, name):
        for block in self.scope_head:
            for key in block.keys():
                if key.lower() == name.lower():
                    return block[key]
        
        for key in self._global_scope.keys():
            if key.lower() == name.lower():
                return self._global_scope[key]
        
        raise SymtabException("Unknown symbol '%s'" % name)


