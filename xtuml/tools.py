# encoding: utf-8
# Copyright (C) 2015 John Törnblom

class Visitor(object):
    '''
    A visitor may be used to visit tree nodes walked by a walker.
    '''
    
    def enter(self, node):
        '''
        Tries to invoke a method matching the pattern *enter_<type name>*, where
        <type name> is the name of the type of the *node*.
        '''
        name = 'enter_' + node.__class__.__name__
        fn = getattr(self, name, self.default_enter)
        fn(node)

    def leave(self, node):
        '''
        Tries to invoke a method matching the pattern *leave_<type name>*, where
        <type name> is the name of the type of the *node*.
        '''
        name = 'leave_' + node.__class__.__name__
        fn = getattr(self, name, self.default_leave)
        fn(node)

    def default_enter(self, node):
        '''
        The default behaviour when entering a *node* if no other action is
        defined by a subclass is to do nothing.
        '''
        pass

    def default_leave(self, node):
        '''
        The default behaviour when leaving a *node* if no other action is
        defined by a subclass is to do nothing.
        '''
        pass
    
    
class Walker(object):
    '''
    A walker may be used to walk a tree.
    '''
    def __init__(self):
        #: A list of *visitors* to notify when visiting nodes.
        self.visitors = list()
        
    def accept(self, node, **kwargs):
        '''
        Invoke the visitors before and after decending down the tree. 
        The walker will also try to invoke a method matching the pattern 
        *accept_<type name>*, where <type name> is the name of the accepted
        *node*.
        '''
        if node is None:
            return
        
        for v in self.visitors:
            v.enter(node)
        
        name = 'accept_' + node.__class__.__name__
        fn = getattr(self, name, self.default_accept)
        r = fn(node, **kwargs)
        
        for v in self.visitors:
            v.leave(node)
        
        return r
    
    def default_accept(self, node, **kwargs):
        '''
        The default accept behaviour is to decend into the iterable member
        *node.children* (if available).
        '''
        if not hasattr(node, 'children'):
            return
        
        for child in node.children:
            self.accept(child, **kwargs)


class NodePrintVisitor(Visitor):
    '''
    A visitor that prints a tree-like structure to stdout.
    '''
    
    def __init__(self):
        self._lvl = 0
        self._suppressed = list()
        
    def default_enter(self, node):
        text = self.render(node)
        if text is None:
            self._suppressed.append(node)
        else:
            print('%s%s' % ("  " * self._lvl, text))
            self._lvl += 1

    def default_leave(self, node):
        if self._suppressed and self._suppressed[-1] == node:
            self._suppressed.pop()
        else:
            self._lvl -= 1
    
    def render(self, node):
        '''
        Try to invoke a method matching the pattern *render_<type name>*, where
        <type name> is the name of the rendering *node*.
        '''
        name = 'render_' + type(node).__name__
        fn = getattr(self, name, self.default_render)
        return fn(node)
        
    def default_render(self, node):
        '''
        The default behaviour when rendering a *node* if no other rendering
        method is defined by a subclass is to render the class name.
        '''
        return type(node).__name__

