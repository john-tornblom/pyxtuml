# encoding: utf-8
# Copyright (C) 2015 John Törnblom

class Node(object):
    '''
    Tree node which may be walked a walker, and visited by a visitor.
    '''
    
    def __str__(self):
        return self.__class__.__name__


class Visitor(object):
    '''
    A visitor may be used to visit tree nodes walked by a walker.
    '''
    
    def enter(self, node):
        name = 'enter_' + node.__class__.__name__
        fn = getattr(self, name, self.default_enter)
        fn(node)

    def leave(self, node):
        name = 'leave_' + node.__class__.__name__
        fn = getattr(self, name, self.default_leave)
        fn(node)

    def default_enter(self, node):
        pass

    def default_leave(self, node):
        pass
    
    
class Walker(object):
    '''
    A walker may be used to walk a tree.
    '''
    
    def __init__(self):
        self.visitors = list()
        
    def accept(self, node, **kwargs):
        if node is None:
            return
        
        for v in self.visitors: v.enter(node)
        
        name = 'accept_' + node.__class__.__name__
        fn = getattr(self, name, self.default_accept)
        r = fn(node, **kwargs)
        
        for v in self.visitors: v.leave(node)
        
        return r
    
    def default_accept(self, node, **kwargs):
        for child in filter(None, node.children):
            self.accept(child, **kwargs)


class NodePrintVisitor(Visitor):
    '''
    A visitor that prints a tree-like structure to stdout.
    '''
    
    def __init__(self):
        self.__lvl = 0
        
    def default_enter(self, node):
        print('%s%s' % ("  " * self.__lvl, node))
        self.__lvl += 1

    def default_leave(self, node):
        self.__lvl -= 1
    
