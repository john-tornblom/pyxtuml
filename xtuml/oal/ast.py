# encoding: utf-8
# Copyright (C) 2014 John Törnblom

class Node(object):
    
    @property
    def children(self):
        return list()

    @property
    def position(self):
        if hasattr(self, '_pos'):
            return self._pos

        min_start = None
        max_stop = None
        for c in filter(None, self.children):
            pos = c.position
            start = pos['start']
            stop = pos['stop']
            
            if not min_start: min_start = start
            if not max_stop: max_stop = stop
            
            min_start = min(min_start, start)
            max_stop = max(max_stop, stop)

        return {'start': min_start, 'stop': max_stop}
        
    def __str__(self):
        return str(self.__class__.__name__[0:-4])


class AbstractListNode(Node):
    
    def __init__(self):
        self._children = list()
        
    @property
    def children(self):
        return self._children


class BodyNode(Node):
    
    def __init__(self, block):
        self.block = block
        
    @property
    def children(self):
        return [self.block]


class BlockNode(AbstractListNode):
    pass


class BreakNode(Node):
    pass


class ReturnNode(Node):
    
    def __init__(self, expr):
        self.expr = expr
        
    @property
    def children(self):
        return [self.expr]


class AssignmentNode(Node):
    
    def __init__(self, lval, rval):
        self.lval = lval
        self.rval = rval
        
    @property
    def children(self):
        return [self.lval, self.rval]


class VariableAccessNode(Node):
    
    def __init__(self, token):
        self.token = token

    @property
    def position(self):
        return self.token.position
    
    def __str__(self):
        return 'VariableAccess (%s)' % repr(self.token)
    
    def __repr__(self):
        return repr(self.token)
    
    
class MemberAccessNode(Node):
    
    def __init__(self, handle, member):
        self.handle = handle
        self.member = member

    @property
    def children(self):
        return [self.handle, self.member]

    def __str__(self):
        return 'MemberAccess (%s)' % repr(self.member)


class EnumAccessNode(Node):
    
    def __init__(self, ty, name):
        self.type = ty
        self.name = name

    @property
    def children(self):
        return [self.type, self.name]

    def __str__(self):
        return 'EnumAccess (%s::%s)' % (repr(self.type), repr(self.name))


class ParamAccessNode(Node):
    
    def __init__(self, member):
        self.member = member

    @property
    def children(self):
        return [self.member]
    
    def __str__(self):
        return 'ParamAccess (%s)' % repr(self.member)


class EventAccessNode(Node):
    
    def __init__(self, member):
        self.member = member

    @property
    def children(self):
        return [self.member]
    
    def __str__(self):
        return 'EventAccess (%s)' % repr(self.member)
    

class LocalVariableNode(Node):
    
    def __init__(self, token):
        self.token = token
        
    @property
    def position(self):
        return self.token.position

    def __str__(self):
        return 'LocalVariable (%s)' % repr(self.token)

    def __repr__(self):
        return repr(self.token)


class ArrayIndexListNode(Node):
    
    def __init__(self):
        self._children = list()
        
    @property
    def children(self):
        return self._children


class IndexedVariableAccessNode(Node):
    
    def __init__(self, var, idx):
        self.var = var
        self.index = idx
        
    @property
    def children(self):
        return [self.var, self.index]


class InstanceLookupNode(Node):
    
    def __init__(self, key_letter, where_clause):
        self.key_letter = key_letter
        self.where_clause = where_clause
        
    @property
    def children(self):
        return [self.where_clause]
    
    def __str__(self):
        return 'InstanceLookup (%s)' % repr(self.key_letter)


class SelectNode(Node):
    
    def __init__(self, variable, spec, ty):
        self.var = variable
        self.spec = spec
        self.type = ty
        
    @property
    def children(self):
        return [self.var, self.spec]
    
    def __str__(self):
        return 'Select (%s)' % repr(self.type)


class InstanceChainNode(Node):
    
    def __init__(self, key_letter, rel_id, phrase, prev):
        self.key_letter = key_letter
        self.rel_id = rel_id
        self.phrase = phrase
        self.prev = prev
    
    @property
    def children(self):
        return [self.prev]
    
    def __str__(self):
        return "InstanceChain (%s[%s]'%s')" % (repr(self.key_letter),
                                               repr(self.rel_id), repr(self.phrase))


class NavigationNode(Node):
    
    def __init__(self, var, chain, where_clause):
        self.var = var
        self.chain = chain
        self.where_clause = where_clause

    @property
    def children(self):
        return [self.var, self.chain, self.where_clause]
    

class RelateNode(Node):
    
    def __init__(self, var1, var2, rel_id, phrase, using):
        self.var1 = var1
        self.var2 = var2
        self.rel_id = rel_id
        self.phrase = phrase
        self.using = using
    
    @property
    def children(self):
        return [self.var1, self.var2, self.using]
    
    def __str__(self):
        if self.phrase:
            return "Relate (%s '%s')" % (repr(self.rel_id), repr(self.phrase))
        else:
            return "Relate (%s)" % repr(self.rel_id)


class UnrelateNode(Node):
    
    def __init__(self, var1, var2, rel_id, phrase, using):
        self.var1 = var1
        self.var2 = var2
        self.rel_id = rel_id
        self.phrase = phrase
        self.using = using

    @property
    def children(self):
        return [self.variable1, self.variable2, self.using]
    
    def __str__(self):
        if self.phrase:
            return "Unrelate (%s '%s')" % (repr(self.rel_id), repr(self.phrase))
        else:
            return "Unrelate (%s)" % repr(self.rel_id)


class DeleteNode(Node):
    
    def __init__(self, variable):
        self.variable = variable

    @property
    def children(self):
        return [self.variable]      


class ParameterListNode(AbstractListNode):
    
    def __repr__(self):
        s = prefix = ''
        for c in self.children: 
            s += prefix + repr(c)
            prefix = ', '
        return s
    

class ParameterNode(Node):
    
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
        
    @property
    def children(self):
        return [self.expr]
    
    def __str__(self):
        return 'Parameter (%s)' % repr(self.name)

    
class InvocationNode(Node):

    def __init__(self, namespace, function, params):
        self.namespace = namespace
        self.function = function
        self.params = params
    
    @property
    def children(self):
        return [self.params]
    
    def __str__(self):
        return 'Invocation (%s::%s)' % (repr(self.namespace), repr(self.function))


class TransformerInvocationNode(Node):
    
    def __init__(self, var, function, params):
        self.var = var
        self.function = function
        self.params = params
        
    @property
    def children(self):
        return [self.var, self.params]
    
    def __str__(self):
        return 'TransformerInvocation (%s)' % repr(self.function)


class BridgeInvocationNode(Node):

    def __init__(self, key_letter, function, params):
        self.key_letter = key_letter
        self.function = function
        self.params = params
    
    @property
    def children(self):
        return [self.params]
    
    def __str__(self):
        return 'BridgeInvocation (%s::%s)' % (repr(self.key_letter), repr(self.function))


class FunctionInvocationNode(Node):

    def __init__(self, function, params):
        self.function = function
        self.params = params
    
    @property
    def children(self):
        return [self.params]
    
    def __str__(self):
        return 'FunctionInvocation (%s)' % repr(self.function)



class MessageInvocationNode(Node):
    
    def __init__(self, port, function, params, target):
        self.port = port
        self.function = function
        self.params = params
        self.target = target
        
    @property
    def children(self):
        return [self.params, self.target]
    
    def __str__(self):
        return 'MessageInvocation (%s::%s)' % (repr(self.port), repr(self.function))


class EventSpecNode(Node):
    
    def __init__(self, label, meaning, params, target):
        self.label = label
        self.meaning = meaning
        self.params = params
        self.target = target
    
    @property
    def children(self):
        return [self.params, self.target]


class CreateObjectNode(Node):
    
    def __init__(self, var, key_letter):
        self.var = var
        self.key_letter = key_letter
        
    @property
    def children(self):
        return [self.var]

    def __str__(self):
        return 'CreateObject (%s)' % repr(self.key_letter)


class CreateEventNode(Node):
    
    def __init__(self, var, spec):
        self.var = var
        self.spec = spec
        
    @property
    def children(self):
        return [self.var, self.spec]


class GenerateNode(Node):
    
    def __init__(self, var):
        self.var = var
        
    @property
    def children(self):
        return [self.var]


class WhileNode(Node):
    
    def __init__(self, expr, block):
        self.expr = expr
        self.block = block
        
    @property
    def children(self):
        return [self.expr, self.block]



class ForEachNode(Node):
    
    def __init__(self, var, set_, block):
        self.var = var
        self.set = set_
        self.block = block
        
    @property
    def children(self):
        return [self.var, self.set, self.block]



class IfNode(Node):
    
    def __init__(self, expr, true_block, false_block=None):
        self.expr = expr
        self.iftrue = true_block
        self.iffalse = false_block
        self.elifs = list()
        
    @property
    def children(self):
        l = [self.expr, self.iftrue]
        l.extend(self.elifs)
        l.append(self.iffalse)
        return l
    

class ElIfNode(Node):
    
    def __init__(self, expr, iftrue):
        self.expr = expr
        self.iftrue = iftrue
        
    @property
    def children(self):
        return [self.expr, self.iftrue]
    

class UnaryOperationNode(Node):
    
    def __init__(self, operand, op):
        self.operand = operand
        self.op = op
        
    @property
    def children(self):
        return [self.operand]
    
    def __str__(self):
        return 'UnaryOperation (%s)' % repr(self.op)


class BinaryOperationNode(Node):
    
    def __init__(self, lhs, op, rhs):
        self.left = lhs
        self.op = op
        self.right = rhs
        
    @property
    def children(self):
        return [self.left, self.right]
    
    def __str__(self):
        return 'BinaryOperation (%s)' % repr(self.op)


class TerminalNode(Node):
    
    def __init__(self, token):
        self.token = token
    
    @property
    def position(self):
        return {'start': (self.token.line, self.token.col),
                'stop' : (self.token.line, self.token.col + len(self.token.text))}
    
    def __str__(self):
        return 'Terminal (%s)' % repr(self)

    def __repr__(self):
        return self.token.text


class IntegerNode(TerminalNode):
        
    def __str__(self):
        return 'Integer (%s)' % repr(self)


class RealNode(TerminalNode):
        
    def __str__(self):
        return 'Real (%s)' % repr(self)


class StringNode(TerminalNode):
    
    def __str__(self):
        return "String ('%s')" % repr(self)
    
    def __repr__(self):
        return repr(self.token.text[1:-1])


class BooleanNode(TerminalNode):
    
    def __str__(self):
        return "Boolean (%s)" % repr(self)
    
    def __repr__(self):
        return self.token.text.lower().capitalize()

