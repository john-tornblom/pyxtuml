# encoding: utf-8
# Copyright (C) 2014 John Törnblom

class Visitor(object):

    def enter(self, inst):
        name = 'enter_' + inst.__class__.__name__
        fn = getattr(self, name, self.default_enter)
        fn(inst)

    def leave(self, inst):
        name = 'leave_' + inst.__class__.__name__
        fn = getattr(self, name, self.default_leave)
        fn(inst)

    def default_enter(self, inst):
        pass

    def default_leave(self, inst):
        pass
    
    
class Walker(object):

    def __init__(self):
        self.visitors = list()
        
    def accept(self, inst, **kwargs):
        for v in self.visitors: v.enter(inst)
        
        name = 'accept_' + inst.__class__.__name__
        fn = getattr(self, name, self.default_accept)
        r = fn(inst, **kwargs)
        
        for v in self.visitors: v.leave(inst)
        
        return r
    
    def default_accept(self, inst, **kwargs):
        for child in inst.children:
            self.accept(child, **kwargs)


class NodePrintVisitor(Visitor):
    
    def __init__(self):
        self.__lvl = 0
        
    def default_enter(self, inst):
        print('%s%s' % ("  " * self.__lvl, inst))
        self.__lvl += 1

    def default_leave(self, inst):
        self.__lvl -= 1
    
