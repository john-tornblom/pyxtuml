# encoding: utf-8
# Copyright (C) 2014 John Törnblom
'''
Abstract syntax tree node definitions for the rule-specification language (RSL).  
'''


from xtuml.tools import Node


#
# Top-level node in a parsed file
#

class BodyNode(Node):
    statement_list = None

    def __init__(self, statement_list):
        self.statement_list = statement_list

#
# Template-related nodes
#    

class LiteralListNode(Node):
    literals = None
    
    def __init__(self):
        self.literals = list()

    def __str__(self):
        return 'LiteralList (%d)' % len(self.literals)


class LiteralNode(Node):
    value = None
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return 'Literal (%s)' % repr(self.value)    


class SubstitutionVariableNode(Node):
    expr = None
    formats = list() 
    
    def __init__(self, fmt, expr):
        self.formats = fmt
        self.expr = expr

    def __str__(self):
        return 'SubstitutionVariable %s' % self.formats


class SubstitutionNavigationNode(Node):
    variable = None
    relation = None
    
    def __init__(self, variable, navigation):
        self.variable = variable
        self.navigation = navigation
        

class ParseKeywordNode(Node):
    expr = None
    keyword = None
    
    def __init__(self, expr, keyword):
        self.expr = expr
        self.keyword = keyword
        

#
# FUnction related nodes
#

class FunctionNode(Node):
    name = None
    parameter_list = None
    statement_list = None

    def __init__(self, name, params, body):
        self.name = name
        self.parameter_list = params
        self.statement_list = body

    def __str__(self):
        return 'Function (%s)' % self.name


class ParameterNode(Node):
    name = None
    type = None

    def __init__(self, ty, name):
        self.name = name
        self.type = ty

    def __str__(self):
        return 'Parameter (%s : %s)' % (self.name, self.type)


class ParameterListNode(Node):
    parameters = list()
    
    def __init__(self):
        self.parameters = list()

    def __str__(self):
        return 'ParameterList (%d)' % len(self.parameters)


class ArgumentListNode(Node):
    arguments = list()
    
    def __init__(self):
        self.arguments = list()

    def __str__(self):
        return 'ArgumentList (%d)' % len(self.arguments)


class StatementListNode(Node):
    statements = list()
    
    def __init__(self):
        self.statements = list()

    def __str__(self):
        return 'StatementList (%d)' % len(self.statements)


#
# Function-like statements
#

class ExitNode(Node):
    return_code = None

    def __init__(self, return_code):
        self.return_code = return_code


class IncludeNode(Node):
    inc_filename = None

    def __init__(self, filename):
        self.inc_filename = filename


class PrintNode(Node):
    value_list = None

    def __init__(self, value_list):
        self.value_list = value_list


class EmitNode(Node):
    emit_filename = None

    def __init__(self, filename):
        self.emit_filename = filename

class ClearNode(Node):
    pass


#
# Assignment statements
#

class AssignNode(Node):
    variable = None
    expr = None

    def __init__(self, variable, expr):
        self.variable = variable
        self.expr = expr

class InvokeNode(Node):
    function_name = None
    argument_list = None
    variable_name = None

    def __init__(self, function_name, args, variable_name=None):
        self.function_name = function_name
        self.argument_list = args
        self.variable_name = variable_name

    def __str__(self):
        return 'Invoke (%s)' % self.function_name


#
# Meta model manipulation statements
#

class CreateNode(Node):
    variable_name = None
    key_letter = None

    def __init__(self, variable_name, key_letter):
        self.variable_name = variable_name
        self.key_letter = key_letter

    def __str__(self):
        return 'Create (%s)' % self.key_letter


class SelectNode(Node):
    variable_name = None
    instance_chain = None
    where = None
    
    def __init__(self, variable_name, instance_chain, where):
        self.variable_name = variable_name
        self.instance_chain = instance_chain
        self.where = where
        
    def __str__(self):
        return '%s (%s)' % (Node.__str__(self), self.variable_name)


class SelectFromNode(Node):
    variable_name = None
    key_letter = None
    where = None
    
    def __init__(self, variable_name, key_letter, where):
        self.variable_name = variable_name
        self.key_letter = key_letter
        self.where = where
        

class SelectAnyInstanceNode(SelectFromNode):
    pass


class SelectManyInstanceNode(SelectFromNode):
    pass


class SelectOneNode(SelectNode):
    pass


class SelectAnyNode(SelectNode):
    pass


class SelectManyNode(SelectNode):
    pass


class WhereNode(Node):
    expr = None
    
    def __init__(self, expr=None):
        self.expr = expr
        

class InstanceChainNode(Node):
    variable = None
    navigations = list()
    
    def __init__(self, variable):
        self.variable = variable
        self.navigations = list()


class NavigationNode(Node):
    key_letter = None
    relation = None
    
    def __init__(self, key_letter, relation):
        self.key_letter = key_letter
        self.relation = relation
        
    def __str__(self):
        return 'Navigation (%s)' % self.key_letter


class RelationNode(Node):
    rel_id = None
    phrase = ''
    
    def __init__(self, rel_id, phrase=''):
        self.rel_id = rel_id
        self.phrase = phrase
        
    def __str__(self):
        return 'Relation (%s)' % self.rel_id


class AlXlateNode(Node):
    activity_type = None
    inst_ref = None

    def __init__(self, activity_type, inst_ref):
        self.activity_type = activity_type
        self.inst_ref = inst_ref

#
# Control flow statements
#

class IfNode(Node):
    cond = None
    iftrue = None
    iffalse = None
    elif_list = None

    def __init__(self, cond, iftrue, elif_list, iffalse):
        self.cond = cond
        self.iftrue = iftrue
        self.elif_list = elif_list
        self.iffalse = iffalse


class ElIfListNode(Node):
    elifs = None
    
    def __init__(self):
        self.elifs = list()

    def __str__(self):
        return 'ElIfList (%d)' % len(self.elifs)


class ElIfNode(Node):
    cond = None
    statement_list = None

    def __init__(self, cond, statement_list):
        self.cond = cond
        self.statement_list = statement_list
    
    
#
# Loop statements
#
    
class ForNode(Node):
    variable_name = None
    set_name = None
    statement_list = None

    def __init__(self, variable_name, set_name, statement_list):
        self.variable_name = variable_name
        self.set_name = set_name
        self.statement_list = statement_list

    def __str__(self):
        return 'For (%s in %s)' % (self.variable_name, self.set_name)


class WhileNode(Node):
    cond = None
    statement_list = None

    def __init__(self, cond, statement_list):
        self.cond = cond
        self.statement_list = statement_list


class BreakNode(Node):
    pass


#
# Expressions
#
    
class BinaryOpNode(Node):
    sign = None
    left = None
    right = None
    
    def __init__(self, left, sign, right):
        self.sign = sign
        self.left = left
        self.right = right
    
    def __str__(self):
        return 'BinaryOp (%s)' % self.sign
    

class UnaryOpNode(Node):
    sign = None
    value = None
    
    def __init__(self, sign, value):
        self.sign = sign
        self.value = value
        
    def __str__(self):
        return 'UnaryOp (%s)' % self.sign
    

class VariableAccessNode(Node):
    name = None
    
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return 'VariableAccess (%s)' % self.name


class FieldAccessNode(Node):
    variable = None
    field = None
    
    def __init__(self, variable, field):
        self.variable = variable
        self.field = field
        
    def __str__(self):
        return 'FieldAccess (%s)' % self.field


class StringBodyNode(Node):
    values = list()
    
    def __init__(self):
        self.values = list()


class StringValueNode(Node):
    value = None
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return 'StringValue (%s)' % repr(self.value)


class IntegerValueNode(Node):
    value = None
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return 'IntegerValue (%s)' % repr(self.value)


class RealValueNode(Node):
    value = None
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return 'RealValue (%s)' % repr(self.value)

