# encoding: utf-8
# Copyright (C) 2014 John Törnblom

def parse(oal_code):
    import OalLexer
    import OalParser

    import StringIO

    l = OalLexer.Lexer(StringIO.StringIO(oal_code))
    l.setText(oal_code)
    
    p = OalParser.Parser(l)
    root = p.action()

    return root

