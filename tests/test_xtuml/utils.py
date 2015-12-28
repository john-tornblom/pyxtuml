# encoding: utf-8
# Copyright (C) 2014-2015 John Törnblom

def expect_exception(exception):
    '''
    Decorator for expecting exceptions to be thrown from a test case
    '''
    def test_decorator(fn):
        def test_decorated(self, *args, **kwargs):
            self.assertRaises(exception, fn, self, *args, **kwargs)
        return test_decorated
    return test_decorator
