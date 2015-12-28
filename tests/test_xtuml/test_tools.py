# encoding: utf-8
# Copyright (C) 2015 John Törnblom
import sys
import unittest

import xtuml.tools


class Node(object):
    '''
    Test Node used for testing xtuml.tools.NodePrintVisitor
    '''
    def __init__(self):
        self.children = list()
        

class TestNodePrinter(unittest.TestCase):
    '''
    Test the walker and visitor in xtuml.tools
    '''
    def test_node(self):
        w = xtuml.tools.Walker()
        w.visitors.append(xtuml.tools.NodePrintVisitor())
        
        root = Node()
        root.children.append(Node())
        root.children.append(Node())
        
        w.accept(root)
        
        s = sys.stdout.getvalue()
        expected  = 'Node\n'
        expected += '  Node\n'
        expected += '  Node\n'
        
        self.assertEqual(s, expected)
        
    def test_generic_class(self):
        w = xtuml.tools.Walker()
        w.visitors.append(xtuml.tools.NodePrintVisitor())
        
        w.accept(self)
        
        s = sys.stdout.getvalue()
        
        self.assertEqual(s, 'TestNodePrinter\n')

    def test_none(self):
        w = xtuml.tools.Walker()
        w.visitors.append(xtuml.tools.NodePrintVisitor())
        
        w.accept(None)
        
        s = sys.stdout.getvalue()
        
        self.assertEqual(s, '')


if __name__ == "__main__":
    unittest.main()

