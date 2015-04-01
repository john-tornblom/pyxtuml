# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import unittest
import xtuml.model
import xtuml.rsl

class RSLTestCase(unittest.TestCase):

    def next_id(self):
        self.current_id += 1
        return self.current_id
    
    def setUp(self):
        self.current_id = 0

        id_generator = xtuml.model.IdGenerator(readfunc=self.next_id)
        self.metamodel = xtuml.model.MetaModel(id_generator)
        self.runtime = xtuml.rsl.runtime.Runtime(self.metamodel)
        self.includes = ['./']
        
    def tearDown(self):
        del self.metamodel

    def eval_text(self, text, filename=''):
        ast = xtuml.rsl.parse_text(text + '\n', filename)
        try:
            xtuml.rsl.evaluate(self.runtime, ast, self.includes)
        except SystemExit as e:
            return e.code

def expect_exception(exception):
    def test_decorator(fn):
        def test_decorated(self, *args, **kwargs):
            self.assertRaises(exception, fn, self, *args, **kwargs)
        return test_decorated
    return test_decorator

def evaluate(f):
    return lambda self: f(self, self.eval_text(f.__doc__, f.__module__ + '.' + f.__name__))

