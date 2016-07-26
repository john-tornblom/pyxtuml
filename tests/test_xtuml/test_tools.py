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


class TestIdGenerator(unittest.TestCase):
    '''
    Test suite for the IdGenerator classes
    '''

    def test_next_pattern(self):
        i = xtuml.IntegerGenerator()
        self.assertEqual(i.peek(), 1)
        self.assertEqual(i.next(), 1)
        self.assertEqual(i.next(), 2)
        self.assertEqual(i.peek(), 3)
        self.assertEqual(i.peek(), 3)

    def test_generator_pattern(self):
        i = xtuml.IntegerGenerator()
        count = 1
        for v in i:
            self.assertEqual(v, count)
            count += 1
            if count == 10:
                break


class TestOrderedSet(unittest.TestCase):
    '''
    Test suite for the class xtuml.OrderedSet
    '''
    
    def test_equal_operator(self):
        s1 = xtuml.OrderedSet()
        s2 = xtuml.OrderedSet()
        
        self.assertEqual(s1, s2)
        
        s1 = xtuml.OrderedSet([1])
        s2 = xtuml.OrderedSet([1])
        
        self.assertEqual(s1, s2)
        
        s1 = xtuml.OrderedSet([1, 2, 3])
        s2 = xtuml.OrderedSet([1, 2, 3])
        
        self.assertEqual(s1, s2)
        self.assertEqual(s1, [1, 2, 3])
        
    def test_not_equal_operator(self):
        s1 = xtuml.OrderedSet()
        s2 = xtuml.OrderedSet([1])
        self.assertNotEqual(s1, s2)
        self.assertNotEqual(s2, s1)
        
        s1 = xtuml.OrderedSet([1, 2, 3])
        s2 = xtuml.OrderedSet([1, 3])
        self.assertNotEqual(s1, s2)
        self.assertNotEqual(s2, s1)
        
        s1 = xtuml.OrderedSet([1, 2, 3])
        s2 = xtuml.OrderedSet([1, 3, 2])
        self.assertNotEqual(s1, s2)
        
    def test_pop_empty(self):
        q = xtuml.OrderedSet()
        self.assertRaises(KeyError, q.pop)

    def test_pop_last(self):
        s1 = xtuml.OrderedSet([1, 2])
        s2 = xtuml.OrderedSet([1])
        self.assertNotEqual(s1, s2)

        s1.pop()
        self.assertEqual(s1, s2)
        
    def test_pop_first(self):
        s1 = xtuml.OrderedSet([2, 1])
        s2 = xtuml.OrderedSet([1])
        self.assertNotEqual(s1, s2)

        s1.pop(last=False)
        self.assertEqual(s1, s2)


if __name__ == "__main__":
    unittest.main()

