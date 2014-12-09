# encoding: utf-8
# Copyright (C) 2014 John Törnblom

def parse(path):
    import SqlLexer
    import SqlParser

    l = SqlLexer.Lexer(path)
    p = SqlParser.Parser(l)
    return p.sql_file()

