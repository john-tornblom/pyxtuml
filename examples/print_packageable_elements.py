#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2016 John Törnblom

import sys
import xtuml

from xtuml import navigate_many as many
from xtuml import navigate_subtype as subtype

from bridgepoint import ooaofooa


class MyWalker(xtuml.Walker):
    '''
    Walk the ooaofooa packageable element tree-like structure
    '''
    
    def accept_S_SYS(self, inst):
        '''
        A System Model contains top-level packages
        '''
        for child in many(inst).EP_PKG[1401]():
            self.accept(child)
    
    def accept_PE_PE(self, inst):
        '''
        Packeable Element is a subtype of something packageable
        '''
        self.accept(subtype(inst, 8001))

    def accept_C_C(self, inst):
        '''
        A Component contains packageable elements
        '''
        for child in many(inst).PE_PE[8003]():
            self.accept(child)
            
    def accept_EP_PKG(self, inst):
        '''
        A Package contains packageable elements
        '''
        for child in many(inst).PE_PE[8000]():
            self.accept(child)


class MyPrinter(xtuml.NodePrintVisitor):

    def render_PE_PE(self, inst):
        '''suppress instances of PE_PE'''
        pass
    
    def render_O_IOBJ(self, inst):
        '''suppress imported classes'''
        pass
    
    def render_R_REL(self, inst):
        return 'R%d (Association)' % inst.Numb
    
    def default_render(self, inst):
        if hasattr(inst, 'Name'):
            return '%s (%s)' % (inst.Name, type(inst).__name__)
        else:
            return type(inst).__name__

    
if len(sys.argv) < 2:
    print('')
    print('  usage: %s <path to bridgepoint model folder>' % sys.argv[0])
    print('')
    sys.exit(1)



m = ooaofooa.load_metamodel(sys.argv[1:])

w = MyWalker()
w.visitors.append(MyPrinter())

for s_sys in m.select_many('S_SYS'):
    w.accept(s_sys)

