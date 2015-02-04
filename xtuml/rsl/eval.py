# encoding: utf-8
# Copyright (C) 2014 John Törnblom
'''
Evaluation of syntax trees constructed from the rule-specification language (RSL).  
'''


import sys
import os
import logging
import traceback

import xtuml.tools
import xtuml.rsl

from . import ast
from . import symtab


logger = logging.getLogger(__name__)


class BreakException(Exception):
    pass


class EvalWalker(xtuml.tools.Walker):
    
    def __init__(self, rt):
        xtuml.tools.Walker.__init__(self)
        self.runtime = rt
        self.callstack = list()
        self.symtab = symtab.SymbolTable()
        
        self.symtab.install_global('true', True)
        self.symtab.install_global('false', False)
        self.symtab.install_global('info', self.runtime.info)
                
        self.symtab.enter_scope()
                    
    def accept(self, node, **kwargs):
        self.runtime.info.arch_file_name = node.filename
        self.runtime.info.arch_file_line = node.lineno

        try:
            return xtuml.tools.Walker.accept(self, node, **kwargs)
        except BreakException as e:
            raise e
        except Exception as e:
            print('Traceback  (most recent call last):')
            for n in self.callstack + [node]:
                print('    File "%s", line %d' % (n.filename, n.lineno))
            print(traceback.format_exc())
            sys.exit(e)
    
    def default_accept(self, node, **kwargs):
        print ('> %s' % node.__class__.__name__)
            
    def accept_BodyNode(self, node):
        assert isinstance(node, ast.BodyNode)
        
        self.accept(node.statement_list)
        
    def accept_FunctionNode(self, node):
        assert isinstance(node, ast.FunctionNode)
        
        def _(fn, *args):
            self.symtab.enter_scope()
            
            self.accept(fn.parameter_list, args=reversed(args))
            for stmt in fn.statement_list.statements:
                self.accept(stmt)

            return self.symtab.leave_scope()
        
        self.runtime.define_function(node.name, lambda *args: _(node, *args))
    
    def accept_ParameterListNode(self, node, args):
        assert isinstance(node, ast.ParameterListNode)
        
        for param, arg in zip (node.parameters, args):
            self.accept(param, arg=arg)

    def accept_ParameterNode(self, node, arg):
        assert isinstance(node, ast.ParameterNode)
        
        self.runtime.assert_type(node.type, arg)
        self.symtab.install_symbol(node.name, arg)

    def accept_InvokeNode(self, node):
        assert isinstance(node, ast.InvokeNode)

        args = self.accept(node.argument_list)
        args = [arg.fget() for arg in args]
        
        self.callstack.append(node)
        value = self.runtime.invoke_function(node.function_name, args)
        self.callstack.pop()
        
        if node.variable_name:
            self.symtab.install_symbol(node.variable_name, value)
    
    def accept_ArgumentListNode(self, node):
        assert isinstance(node, ast.ArgumentListNode)
        
        return [self.accept(arg) for arg in node.arguments]

    def accept_StatementListNode(self, node):
        assert isinstance(node, ast.StatementListNode)
        
        for stmt in node.statements:
            self.accept(stmt)
            
    def accept_AssignNode(self, node):
        assert isinstance(node, ast.AssignNode)
        
        value = self.accept(node.expr).fget()
        variable = self.accept(node.variable, mode='w')
        variable.fset(value)
        
    def accept_StringBodyNode(self, node):
        assert isinstance(node, ast.StringBodyNode)
        
        s = ''
        for value in node.values:
            s += self.accept(value).fget()
            
        return property(lambda: s)
    
    def accept_StringValueNode(self, node):
        assert isinstance(node, ast.StringValueNode)
        
        s = node.value
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        
        return property(lambda: s)
        
    def accept_IntegerValueNode(self, node):
        assert isinstance(node, ast.IntegerValueNode)
        
        i = int(node.value)
        
        return property(lambda: i)
        
    def accept_RealValueNode(self, node):
        assert isinstance(node, ast.RealValueNode)
        
        i = float(node.value)
        
        return property(lambda: i)
        
    def accept_VariableAccessNode(self, node, mode='r'):
        assert isinstance(node, ast.VariableAccessNode)
        
        fget = fset = None
        if 'r' in mode:
            value = self.symtab.find_symbol(node.name)
            fget = lambda: value
        if 'w' in mode:
            fset = lambda value: self.symtab.install_symbol(node.name, value)
            
        return property(fget, fset)
    
    def accept_FieldAccessNode(self, node, mode='r'):
        assert isinstance(node, ast.FieldAccessNode)
        
        variable = self.accept(node.variable).fget()
        
        fget = fset = None
        if 'r' in mode:
            fget = lambda: getattr(variable, node.field)    
        if 'w' in mode:
            fset = lambda value: setattr(variable, node.field, value)
            
        return property(fget, fset)
    
    def accept_SubstitutionVariableNode(self, node):
        assert isinstance(node, ast.SubstitutionVariableNode)
        
        value = self.accept(node.expr).fget()
        value = self.runtime.format_string(value, node.formats)

        return property(lambda: value)
    
    def accept_SubstitutionNavigationNode(self, node):
        assert isinstance(node, ast.SubstitutionNavigationNode)
        
        variable = self.accept(node.variable).fget()
        chain = self.runtime.chain(variable)
        
        key_letter = node.navigation.key_letter
        rel_id = node.navigation.relation.rel_id
        phrase = node.navigation.relation.phrase
        
        inst_set = chain.nav(key_letter, rel_id, phrase)()
        value = self.runtime.select_any_in(inst_set, lambda selected: True)
        
        return property(lambda: value)
    
    def accept_ParseKeywordNode(self, node):
        assert isinstance(node, ast.ParseKeywordNode)
        
        keyword = self.accept(node.keyword).fget()
        value = self.accept(node.expr).fget()
        value = self.runtime.parse_keyword(value, keyword)
        
        return property(lambda: value)
    
    def accept_PrintNode(self, node):
        assert isinstance(node, ast.PrintNode)
        
        value = self.accept(node.value_list).fget()
        self.runtime.invoke_print(value)

    def accept_ExitNode(self, node):
        assert isinstance(node, ast.ExitNode)
        
        value = self.accept(node.return_code).fget()
        self.runtime.invoke_exit(value)
        
    def accept_IfNode(self, node):
        assert isinstance(node, ast.IfNode)
        
        try:
            self.symtab.enter_block()
            if self.accept(node.cond).fget():
                self.accept(node.iftrue)
            elif not self.accept(node.elif_list).fget():
                self.accept(node.iffalse)
            self.symtab.leave_block()
        except BreakException as e:
            self.symtab.leave_block()
            raise e
                        
    def accept_ElIfListNode(self, node):
        assert isinstance(node, ast.ElIfListNode)
        
        b = False
        for _elif in node.elifs:
            b = self.accept(_elif).fget()
            if b: break
            
        return property(lambda: b)
    
    def accept_ElIfNode(self, node):
        assert isinstance(node, ast.ElIfNode)
        
        b = self.accept(node.cond).fget()
        if b:
            self.accept(node.statement_list)

        return property(lambda: b)
    
    def accept_WhileNode(self, node):
        assert isinstance(node, ast.WhileNode)
        
        try:
            self.symtab.enter_block()
            while self.accept(node.cond).fget():
                self.accept(node.statement_list)
            self.symtab.leave_block()
        except BreakException:
            self.symtab.leave_block()
        
    def accept_ForNode(self, node):
        assert isinstance(node, ast.ForNode)
        
        try:
            self.symtab.enter_block()
            for value in iter(self.symtab.find_symbol(node.set_name)):
                self.symtab.install_symbol('selected', value)
                self.symtab.install_symbol(node.variable_name, value)
                self.accept(node.statement_list)
            self.symtab.leave_block()
        except BreakException:
            self.symtab.leave_block()

    def accept_BreakNode(self, node):
        assert isinstance(node, ast.BreakNode)
        
        raise BreakException()

    def accept_BinaryOpNode(self, node):
        assert isinstance(node, ast.BinaryOpNode)
        
        ops = {
            '|':   lambda lhs, rhs: (lhs | rhs),
            '&':   lambda lhs, rhs: (lhs & rhs),
            '+':   lambda lhs, rhs: (lhs + rhs),
            '-':   lambda lhs, rhs: (lhs - rhs),
            '*':   lambda lhs, rhs: (lhs * rhs),
            '/':   lambda lhs, rhs: (lhs / rhs),
            '<':   lambda lhs, rhs: (lhs < rhs),
            '<=':  lambda lhs, rhs: (lhs <= rhs),
            '>':   lambda lhs, rhs: (lhs > rhs),
            '>=':  lambda lhs, rhs: (lhs >= rhs),
            '!=':  lambda lhs, rhs: (lhs != rhs),
            '==':  lambda lhs, rhs: (lhs == rhs),
            'or':  lambda lhs, rhs: (lhs or  rhs),
            'and': lambda lhs, rhs: (lhs and rhs),
        }

        lhs = self.accept(node.left).fget()
        rhs = self.accept(node.right).fget()
        
        if node.sign in ['|', '&']:
            lhs = self.runtime.cast_to_set(lhs)
            
        if isinstance(lhs, xtuml.model.QuerySet):
            rhs = self.runtime.cast_to_set(rhs)
            
        value = ops[node.sign](lhs, rhs)
        
        return property(lambda: value)
    
    def accept_UnaryOpNode(self, node):
        assert isinstance(node, ast.UnaryOpNode)
        
        ops = {
            '-':           lambda value:-value,
            'not':         lambda value: not value,
            'cardinality': lambda value: self.runtime.cardinality(value),
            'empty':       lambda value: self.runtime.empty(value),
            'first':       lambda value: self.runtime.first(self.symtab.find_symbol('selected'), value),
            'last':        lambda value: self.runtime.last(self.symtab.find_symbol('selected'), value),
            'not_empty':   lambda value: self.runtime.not_empty(value),
            'not_first':   lambda value: self.runtime.not_first(self.symtab.find_symbol('selected'), value),
            'not_last':    lambda value: self.runtime.not_last(self.symtab.find_symbol('selected'), value),
        }

        value = self.accept(node.value).fget()
        value = ops[node.sign](value)
        
        return property(lambda: value)
    
    def accept_LiteralNode(self, node):
        assert isinstance(node, ast.LiteralNode)
        
        s = node.value
        
        return property(lambda: s)
    
    def accept_LiteralListNode(self, node):
        assert isinstance(node, ast.LiteralListNode)
        
        s = ''
        for literal in node.literals:
            s += self.accept(literal).fget()
         
        self.runtime.buffer_literal(s)
        
    def accept_EmitNode(self, node):
        assert isinstance(node, ast.EmitNode)
        
        filename = self.accept(node.emit_filename).fget()
        
        self.runtime.emit_buffer(filename)
    
    def accept_ClearNode(self, node):
        assert isinstance(node, ast.ClearNode)
        
        self.runtime.clear_buffer()
            
    def accept_IncludeNode(self, node):
        assert isinstance(node, ast.IncludeNode)
        
        filename = self.accept(node.inc_filename).fget()
        if filename in self.runtime.include_cache:
            root = self.runtime.include_cache[filename]
        
        elif os.path.exists(filename):
            root = xtuml.rsl.parse_file(filename)
            self.runtime.include_cache[filename] = root
            
        elif not os.path.isabs(filename):
            path = os.path.dirname(self.runtime.info.arch_file_name)
            if not path: path = '.'
            root = xtuml.rsl.parse_file('%s/%s' % (path, filename))
            self.runtime.include_cache[filename] = root
        else:
            raise Exception("unable to find '%s'" % filename)
        
        self.callstack.append(node)
        self.accept(root)
        self.callstack.pop()
        
    def accept_CreateNode(self, node):
        assert isinstance(node, ast.CreateNode)
        
        inst = self.runtime.new(node.key_letter)
        self.symtab.install_symbol(node.variable_name, inst)
        
        return property(lambda: inst)
        
    def accept_SelectAnyInstanceNode(self, node):
        assert isinstance(node, ast.SelectAnyInstanceNode)
        
        where = self.accept(node.where)
        value = self.runtime.select_any_from(node.key_letter, where)
        
        self.symtab.install_symbol(node.variable_name, value)
        
        return property(lambda: value)
        
    def accept_SelectManyInstanceNode(self, node):
        assert isinstance(node, ast.SelectManyInstanceNode)

        where = self.accept(node.where)
        value = self.runtime.select_many_from(node.key_letter, where)
        
        self.symtab.install_symbol(node.variable_name, value)
        
        return property(lambda: value)

    def accept_SelectOneNode(self, node):
        assert isinstance(node, ast.SelectOneNode)
        
        inst_set = iter(self.accept(node.instance_chain).fget())
        where = self.accept(node.where)
        value = self.runtime.select_one_in(inst_set, where)
        
        self.symtab.install_symbol(node.variable_name, value)
        
        return property(lambda: value)

    def accept_SelectAnyNode(self, node):
        assert isinstance(node, ast.SelectAnyNode)
        
        inst_set = iter(self.accept(node.instance_chain).fget())
        where = self.accept(node.where)
        value = self.runtime.select_any_in(inst_set, where)
        
        self.symtab.install_symbol(node.variable_name, value)
        
        return property(lambda: value)
        
    def accept_SelectManyNode(self, node):
        assert isinstance(node, ast.SelectManyNode)
        
        inst_set = iter(self.accept(node.instance_chain).fget())
        where = self.accept(node.where)
        value = self.runtime.select_many_in(inst_set, where)
        
        self.symtab.install_symbol(node.variable_name, value)
        
        return property(lambda: value)

    def accept_WhereNode(self, node):
        assert isinstance(node, ast.WhereNode)
        
        def where(expr, selected):
            if node.expr is None: return True
            
            self.symtab.enter_block()
            self.symtab.install_symbol('selected', selected)
            value = self.accept(expr).fget()
            self.symtab.leave_block()
            
            return value
            
        return lambda selected: where(node.expr, selected)
        
    def accept_InstanceChainNode(self, node):
        assert isinstance(node, ast.InstanceChainNode)
        
        inst = self.accept(node.variable).fget()
        chain = self.runtime.chain(inst)
        
        for nav in node.navigations:
            rel_id = nav.relation.rel_id
            phrase = nav.relation.phrase
            chain = chain.nav(nav.key_letter, rel_id, phrase)
        
        result = chain()
        
        return property(lambda: result)
    
    
