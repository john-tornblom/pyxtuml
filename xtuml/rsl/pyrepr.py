# encoding: utf-8
# Copyright (C) 2014 John Törnblom
'''
Python translation of syntax trees constructed from the rule-specification language (RSL).
NOTE: Not fully working due to scope issues when including files.
'''

import types
import logging

import xtuml.tools


from . import ast


logger = logging.getLogger(__name__)


class PyReprWalker(xtuml.tools.Walker):

        
    keywords = ('and', 
                'del',
                'from',
                'not',
                'while',
                'as',
                'elif',
                'global',
                'or',
                'with',
                'assert',
                'else',
                'if',
                'pass',
                'yield',
                'break',
                'except',
                'import',
                'print',
                'class',
                'exec',
                'in',
                'raise',
                'continue',
                'finally',
                'is',
                'return',
                'def',
                'for',
                'lambda',
                'try')
        
    def __init__(self, runtime):
        xtuml.tools.Walker.__init__(self)
        self.runtime = runtime
        self._lvl = 0
        
    def enter_block(self):
        self._lvl += 1
        
    def leave_block(self):
        self._lvl -= 1
    
    @property
    def linebreak(self):
        return '\n' + ('    ' * self._lvl)
    
    def get_safe_identifier(self, name):
        if name in self.keywords:
            return name.title()
        elif name is None:
            return '_'
        else:
            return name
            
    def default_accept(self, node, **kwargs):
        print ('> %s' % node.__class__.__name__)
            
    def accept_BodyNode(self, node):
        assert isinstance(node, ast.BodyNode)
        
        s = '_rt.info.arch_file_name = %s' % repr(node.filename)
        s += self.linebreak + self.accept(node.statement_list) 
        
        return s
        
    def accept_FunctionNode(self, node):
        assert isinstance(node, ast.FunctionNode)
        
        name = node.name
        params = self.accept(node.parameter_list)
        
        self.enter_block()
        body = self.accept(node.statement_list)
        body += self.linebreak + 'return locals()'
        self.leave_block()
        
        py_code = 'def _%s%s' % (params, body)
        code = compile(py_code, '<string>', 'exec')
        globs = globals()
        globs['_rt'] = self.runtime
        
        fn = types.FunctionType(code.co_consts[0], globs, name)
        self.runtime.define_function(name, fn)
        
        return ''
    
    def accept_ParameterListNode(self, node):
        assert isinstance(node, ast.ParameterListNode)
        
        s = prefix = ''
        for param in reversed(node.parameters):
            s += prefix
            s += self.get_safe_identifier(param.name)
            prefix = ', '

        s = '(%s):' % s
        
        self.enter_block()
        
        for param in reversed(node.parameters):
            arg = self.get_safe_identifier(param.name)
            s += self.linebreak
            s += '_rt.assert_type(%s, %s)' % (repr(param.type), arg)
        
        self.leave_block()
        
        return s

    def accept_InvokeNode(self, node):
        assert isinstance(node, ast.InvokeNode)

        variable = self.get_safe_identifier(node.variable_name)
        
        name = repr(node.function_name)
        args = self.accept(node.argument_list)
        
        return '%s = _rt.invoke_function(%s, %s)' % (variable, name, args) 
    
    def accept_ArgumentListNode(self, node):
        assert isinstance(node, ast.ArgumentListNode)
        
        s = ''
        for argument in node.arguments:
            s += self.accept(argument) + ', '

        return '(%s)' % s

    def accept_StatementListNode(self, node):
        assert isinstance(node, ast.StatementListNode)
        
        s = ''
        for stmt in node.statements:
            s += self.linebreak + '_rt.info.arch_file_line = %s' % repr(stmt.lineno)
            s += self.linebreak + self.accept(stmt)
        
        if not s:
            s = self.linebreak + 'pass'
        
        return s
    
    def accept_AssignNode(self, node):
        assert isinstance(node, ast.AssignNode)
        
        value = self.accept(node.expr)
        variable = self.accept(node.variable)
        
        return '%s = %s' % (variable, value)        
        
        
    def accept_StringBodyNode(self, node):
        assert isinstance(node, ast.StringBodyNode)
        
        s = prefix = ''
        for value in node.values:
            s += prefix + self.accept(value)
            prefix = " + "
        
        if not s: s = repr(s)
        
        return s
    
    def accept_StringValueNode(self, node):
        assert isinstance(node, ast.StringValueNode)
        
        s = node.value
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        
        return repr(s) 
        
    def accept_IntegerValueNode(self, node):
        assert isinstance(node, ast.IntegerValueNode)
        
        return node.value
        
    def accept_RealValueNode(self, node):
        assert isinstance(node, ast.RealValueNode)
        
        return node.value
        
    def accept_VariableAccessNode(self, node):
        assert isinstance(node, ast.VariableAccessNode)
        
        renames = {
            'true': 'True',
            'false': 'False',
            'info': '_rt.info'
        }

        if node.name.lower() in renames:
            return renames[node.name.lower()]
        else: 
            return self.get_safe_identifier(node.name)
    
    def accept_FieldAccessNode(self, node):
        assert isinstance(node, ast.FieldAccessNode)
        
        variable = self.accept(node.variable)
        field = self.get_safe_identifier(node.field)
        
        return '%s.%s' % (variable, field)
    
    def accept_SubstitutionVariableNode(self, node):
        assert isinstance(node, ast.SubstitutionVariableNode)
        
        expr = self.accept(node.expr)
        fmt = node.formats
        
        return '_rt.format_string(%s, %s)' % (expr, fmt)
    
    def accept_SubstitutionNavigationNode(self, node):
        assert isinstance(node, ast.SubstitutionNavigationNode)
        
        chain = '_rt.chain(%s)' % self.accept(node.variable)
        
        key_letter = repr(node.navigation.key_letter)
        rel_id = repr(node.navigation.relation.rel_id)
        phrase = repr(node.navigation.relation.phrase)
        nav = 'nav(%s, %s, %s)' % (key_letter, rel_id, phrase)
        
        return '_rt.select_any_in(%s.%s(), lambda selected: True)' % (chain, nav)
    
    def accept_ParseKeywordNode(self, node):
        assert isinstance(node, ast.ParseKeywordNode)
        
        keyword = self.accept(node.keyword)
        expr = self.accept(node.expr)
        
        return '_rt.parse_keyword(%s, %s)' % (expr, keyword)
    
    def accept_PrintNode(self, node):
        assert isinstance(node, ast.PrintNode)
        
        value = self.accept(node.value_list)
        
        return '_rt.invoke_print(%s)' % value

    def accept_ExitNode(self, node):
        assert isinstance(node, ast.ExitNode)
        
        return_code = self.accept(node.return_code)
        
        return '_rt.invoke_exit(%s)' % return_code
        
    def accept_IfNode(self, node):
        assert isinstance(node, ast.IfNode)
        
        cond = self.accept(node.cond)
        
        self.enter_block()
        iftrue = self.accept(node.iftrue)
        self.leave_block()
        
        elifs = self.accept(node.elif_list)
        
        self.enter_block()
        iffalse = self.accept(node.iffalse)
        self.leave_block()
        
        s = 'if %s:%s' % (cond, iftrue)
        s += elifs
        if iffalse:
            s += self.linebreak + 'else:%s' % iffalse
        
        return s
                        
    def accept_ElIfListNode(self, node):
        assert isinstance(node, ast.ElIfListNode)
        
        s = ''
        for _elif in node.elifs:
            s += self.linebreak + self.accept(_elif)
            
        return s
    
    def accept_ElIfNode(self, node):
        assert isinstance(node, ast.ElIfNode)
        
        s = 'elif %s:' % self.accept(node.cond)
        
        self.enter_block()
        s += self.accept(node.statement_list)
        self.leave_block()
        
        return s
    
    def accept_WhileNode(self, node):
        assert isinstance(node, ast.WhileNode)
        
        s = 'while %s:' % self.accept(node.cond)
        
        self.enter_block()
        s += self.accept(node.statement_list)
        self.leave_block()
        
        return s
        
    def accept_ForNode(self, node):
        assert isinstance(node, ast.ForNode)
        
        inst_name = self.get_safe_identifier(node.variable_name)
        set_name = self.get_safe_identifier(node.set_name)
        
        s = 'for %s in %s:' % (inst_name, set_name)
        
        self.enter_block()
        s += self.linebreak + 'selected = %s' % inst_name
        s += self.accept(node.statement_list)
        self.leave_block()
        
        return s
        

    def accept_BreakNode(self, node):
        assert isinstance(node, ast.BreakNode)
        
        return 'break'

    def accept_BinaryOpNode(self, node):
        assert isinstance(node, ast.BinaryOpNode)
        
        sign = node.sign
        lhs = self.accept(node.left)
        rhs = self.accept(node.right)
        
        if node.sign in ['|', '&']:
            lhs = '_rt.cast_to_set(%s)' % lhs
            rhs = '_rt.cast_to_set(%s)' % rhs
            
        return '(%s %s %s)' % (lhs, sign, rhs)
    
    def accept_UnaryOpNode(self, node):
        assert isinstance(node, ast.UnaryOpNode)
        
        sign = node.sign.lower()
        value = self.accept(node.value)
        
        if sign in ['not', '-']:
            return '(%s %s)' % (sign, value)
        
        elif sign in ['first', 'not_first', 'last', 'not_last']:
            return '_rt.%s(selected, %s)' % (sign, value)
         
        else:
            return '_rt.%s(%s)' % (sign, value)
    
    def accept_LiteralNode(self, node):
        assert isinstance(node, ast.LiteralNode)
        
        return repr(node.value)
    
    def accept_LiteralListNode(self, node):
        assert isinstance(node, ast.LiteralListNode)
        
        s = prefix = ''
        for literal in node.literals:
            s = s + prefix + self.accept(literal)
            prefix = ' + '
        
        s = "_rt.buffer_literal(%s)" % s
        
        return s
        
    def accept_EmitNode(self, node):
        assert isinstance(node, ast.EmitNode)
        
        filename = self.accept(node.emit_filename)
        
        return "_rt.emit_buffer(%s)" % filename
    
    def accept_ClearNode(self, node):
        assert isinstance(node, ast.ClearNode)
        
        return '_rt.clear_buffer()'
            
    def accept_IncludeNode(self, node):
        assert isinstance(node, ast.IncludeNode)
        
        filename = self.accept(node.inc_filename)
        
        return 'exec(_rt.compile(%s))' % filename
        
    def accept_CreateNode(self, node):
        assert isinstance(node, ast.CreateNode)
        
        variable = self.get_safe_identifier(node.variable_name)
        key_letter = node.key_letter
            
        return '%s = _rt.new("%s")' % (variable, key_letter)
        
    def accept_SelectAnyInstanceNode(self, node):
        assert isinstance(node, ast.SelectAnyInstanceNode)
        
        variable = self.get_safe_identifier(node.variable_name)
        key_letter = repr(node.key_letter)
        where = self.accept(node.where)
        
        return '%s = _rt.select_any_from(%s, %s)' % (variable, key_letter, where)
        
    def accept_SelectManyInstanceNode(self, node):
        assert isinstance(node, ast.SelectManyInstanceNode)

        variable = self.get_safe_identifier(node.variable_name)
        key_letter = repr(node.key_letter)
        where = self.accept(node.where)
            
        return '%s = _rt.select_many_from(%s, %s)' % (variable, key_letter, where)
        
    def accept_SelectOneNode(self, node):
        assert isinstance(node, ast.SelectOneNode)
        
        variable = self.get_safe_identifier(node.variable_name)
        nav = self.accept(node.instance_chain)
        where = self.accept(node.where)

        return '%s = _rt.select_one_in(%s, %s)' % (variable, nav, where)

    def accept_SelectAnyNode(self, node):
        assert isinstance(node, ast.SelectAnyNode)
        
        variable = self.get_safe_identifier(node.variable_name)
        nav = self.accept(node.instance_chain)
        where = self.accept(node.where)

        return '%s = _rt.select_any_in(%s, %s)' % (variable, nav, where)
        
    def accept_SelectManyNode(self, node):
        assert isinstance(node, ast.SelectManyNode)
        
        variable = self.get_safe_identifier(node.variable_name)
        nav = self.accept(node.instance_chain)
        where = self.accept(node.where)

        return '%s = _rt.select_many_in(%s, %s)' % (variable, nav, where)
        
    def accept_WhereNode(self, node):
        assert isinstance(node, ast.WhereNode)
        
        if node.expr is None:
            cond = 'True'
        else:
            cond = self.accept(node.expr)
        
        return 'lambda selected: %s' % cond
        
        
    def accept_InstanceChainNode(self, node):
        assert isinstance(node, ast.InstanceChainNode)
        
        chain = '_rt.chain(%s)' % self.accept(node.variable)
        
        for nav in node.navigations:
            key_letter = repr(nav.key_letter)
            rel_id = repr(nav.relation.rel_id)
            phrase = repr(nav.relation.phrase)
            chain += '.nav(%s, %s, %s)' % (key_letter, rel_id, phrase)
        
        return '%s()' % chain
    
    
