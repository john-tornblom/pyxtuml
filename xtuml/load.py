# encoding: utf-8
# Copyright (C) 2015 John Törnblom

'''
Loading support for xtUML models (based on sql).
'''

import uuid
import logging
import os

from ply import lex
from ply import yacc

from xtuml import model


logger = logging.getLogger(__name__)


class ParsingException(Exception):
    pass


class CreateInstanceStmt(object):
    
    def __init__(self, kind, values):
        self.kind = kind
        self.values = values

        
class CreateClassStmt(object):
    
    def __init__(self, kind, attributes):
        self.kind = kind
        self.attributes = attributes
        

class CreateRelatationStmt(object):
    
    def __init__(self, ass1, ass2, rel_id):
        self.end_points = (ass1, ass2)
        self.id = rel_id
        

class ModelLoader(object):
    '''
    Lexer and parser for xtUML models (based on sql).
    '''
    reserved = (
        'CREATE',
        'INSERT',
        'INTO',
        'VALUES',
        'TABLE',
        'ROP',
        'REF_ID',
        'FROM',
        'TO',
        'PHRASE'
    )

    tokens = reserved + (
        'COMMA',
        'FRACTION',
        'GUID',
        'ID',
        'LPAREN',
        'MINUS',
        'NUMBER',
        'RPAREN',
        'RELID',
        'SEMICOLON',
        'STRING',
        'CARDINALITY',
    )

    # A string containing ignored characters (spaces and tabs).
    t_ignore = ' \t\r\x0c'

    parser = None
    lexer = None
    statements = None
    
    def __init__(self):
        self.statements = list()
        
        self.lexer = lex.lex(debuglog=logger,
                             errorlog=logger,
                             optimize=1,
                             module=self,
                             outputdir=os.path.dirname(__file__),
                             lextab="xtuml.__xtuml_lextab")
        
        self.parser = yacc.yacc(debuglog=logger,
                                errorlog=logger,
                                optimize=1,
                                module=self,
                                outputdir=os.path.dirname(__file__),
                                tabmodule='xtuml.__xtuml_parsetab')

    def build_parser(self):
        '''
        This method is deprecated.
        '''
        pass
    
    def input(self, data):
        '''
        Parse input as raw data.
        '''
        s = self.parser.parse(lexer=self.lexer, input=data)
        self.statements.extend(s)
    

    def filename_input(self, filename):
        '''
        Open and read a filename, and parse its content.
        '''
        with open(filename, 'r') as f:
            return self.file_input(f)
    
    
    def file_input(self, f):
        '''
        Read and parse data from a file handle.
        '''
        return self.input(f.read())


    def build_metamodel(self, id_generator=None, ignore_undefined_classes=False):
        '''
        Build and return a meta model from previously parsed input.
        '''
        m = model.MetaModel(id_generator)
        m.ignore_undefined_classes = ignore_undefined_classes
        
        schema = [s for s in self.statements if isinstance(s, CreateClassStmt)]
        relations = [s for s in self.statements if isinstance(s, CreateRelatationStmt)]
        instances = [s for s in self.statements if isinstance(s, CreateInstanceStmt)]
        
        for s in schema:
            m.define_class(s.kind, s.attributes)
        
        for s in relations:
            end1, end2 = s.end_points
            m.define_relation(s.id, end1, end2)
            
        for s in instances:
            m.new(s.kind, *s.values)
            
        return m

    def t_comment(self, t):
        r'\-\-([^\n]*\n)'
        t.lexer.lineno += (t.value.count("\n"))
        t.endlexpos = t.lexpos + len(t.value)

    def t_COMMA(self, t):
        r','
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_FRACTION(self, t):
        r'(\d+)(\.\d+)'
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_RELID(self, t):
        r'R[0-9]+'
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_CARDINALITY(self, t):
        r'(1C)'
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_ID(self, t):
        r'[A-Za-z_][\w_]*'
        if t.value in self.reserved:
            t.type = t.value
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_LPAREN(self, t):
        r'\('
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_MINUS(self, t):
        r'-'
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_NUMBER(self, t):
        r'[0-9]+'
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_RPAREN(self, t):
        r'\)'
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_SEMICOLON(self, t):
        r';'
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_STRING(self, t):
        r'\'((\'\')|[^\'])*\''
        t.lexer.lineno += (t.value.count("\n"))
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_GUID(self, t):
        r'\"([^\\\n]|(\\.))*?\"'
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        t.endlexpos = t.lexpos + len(t.value)

    def t_error(self, t):
        logger.error("line %d: Illegal character '%s'" % (t.lineno, t.value[0]))

    def p_translation_unit(self, p):
        '''translation_unit : statement_list'''
        p[0] = p[1]

    def p_statement_list_1(self, p):
        '''statement_list : statement'''
        p[0] = [p[1]]

    def p_statement_list_2(self, p):
        '''statement_list : statement_list statement'''
        p[0] = p[1] + [p[2]]

    def p_statement_1(self, p):
        '''statement : create_table_statement SEMICOLON'''
        p[0] = p[1]

    def p_statement_2(self, p):
        '''statement : insert_into_statement SEMICOLON'''
        p[0] = p[1]

    def p_statement_3(self, p):
        '''statement : create_rop_statement SEMICOLON'''
        p[0] = p[1]

    def p_create_table_statement(self, p):
        '''create_table_statement : CREATE TABLE ident LPAREN attr_list RPAREN'''
        p[0] = CreateClassStmt(p[3].upper(), p[5])

    def p_attr_list_1(self, p):
        '''attr_list : attr'''
        p[0] = [p[1]]

    def p_attr_list_2(self, p):
        '''attr_list : attr_list COMMA attr'''
        p[0] = p[1] + [p[3]]

    def p_attr_list_3(self, p):
        '''attr_list : '''
        p[0] = []

    def p_attr(self, p):
        '''attr : ident ident'''
        p[0] = (p[1], p[2])

    def p_insert_into_statement(self, p):
        '''
        insert_into_statement : INSERT INTO ident VALUES LPAREN value_list RPAREN
        '''
        p[0] = CreateInstanceStmt(p[3].upper(), p[6])

    def p_value_list_1(self, p):
        '''value_list : value'''
        p[0] = [p[1]]

    def p_value_list_2(self, p):
        '''value_list : value_list COMMA value'''
        p[0] = p[1] + [p[3]]

    def p_value_list_3(self, p):
        '''value_list : '''
        p[0] = []
        
    def p_value_1(self, p):
        '''value : FRACTION'''
        p[0] = float(p[1])

    def p_value_2(self, p):
        '''value : MINUS FRACTION'''
        p[0] = -float(p[2])

    def p_value_3(self, p):
        '''value : NUMBER'''
        p[0] = int(p[1])

    def p_value_4(self, p):
        '''value : MINUS NUMBER'''
        p[0] = -int(p[2])

    def p_value_5(self, p):
        '''value : STRING'''
        p[0] = str(p[1].replace("''", "'")[1:-1])

    def p_value_6(self, p):
        '''value : GUID'''
        p[0] = uuid.UUID(p[1][1:-1]).int

    def p_create_rop_statement(self, p):
        '''
        create_rop_statement : CREATE ROP REF_ID RELID FROM association_end TO association_end
        '''
        p[0] = CreateRelatationStmt(p[6], p[8], p[4])

    def p_association_end_1(self, p):
        '''association_end : cardinality ident LPAREN id_list RPAREN'''
        p[0] = model.AssociationLink(p[2].upper(), p[1], p[4])

    def p_association_end_2(self, p):
        '''association_end : cardinality ident LPAREN id_list RPAREN PHRASE STRING'''
        p[0] = model.AssociationLink(p[2].upper(), p[1], p[4], p[7][1:-1])

    def p_cardinality_1(self, p):
        '''cardinality : NUMBER'''
        if p[1] != '1':
            raise ParsingException("invalid cardinality '%s' at (%s, %d)" % (p[1], p.lineno(1), p.lexpos(1)))
        p[0] = p[1]

    def p_cardinality_2(self, p):
        '''cardinality : ID'''
        if p[1] not in ['M', 'MC']:
            raise ParsingException("invalid cardinality '%s' at (%s, %d)" % (p[1], p.lineno(1), p.lexpos(1)))
        p[0] = p[1]

    def p_cardinality_3(self, p):
        '''cardinality : CARDINALITY'''
        p[0] = p[1]

    def p_id_list_1(self, p):
        '''id_list : ident'''
        p[0] = [p[1]]

    def p_id_list_2(self, p):
        '''id_list : id_list COMMA ident'''
        p[0] = p[1] + [p[3]]

    def p_id_list_3(self, p):
        '''id_list : '''
        p[0] = []

    def p_idend_1(self, p):
        '''ident : ID'''
        p[0] = p[1]

    def p_idend_2(self, p):
        '''ident : CREATE'''
        p[0] = p[1]

    def p_idend_3(self, p):
        '''ident : INSERT'''
        p[0] = p[1]

    def p_idend_4(self, p):
        '''ident : INTO'''
        p[0] = p[1]

    def p_idend_5(self, p):
        '''ident : VALUES'''
        p[0] = p[1]

    def p_idend_6(self, p):
        '''ident : TABLE'''
        p[0] = p[1]

    def p_idend_7(self, p):
        '''ident : ROP'''
        p[0] = p[1]

    def p_idend_8(self, p):
        '''ident : REF_ID'''
        p[0] = p[1]

    def p_idend_9(self, p):
        '''ident : FROM'''
        p[0] = p[1]

    def p_idend_10(self, p):
        '''ident : TO'''
        p[0] = p[1]

    def p_idend_11(self, p):
        '''ident : PHRASE'''
        p[0] = p[1]

    def p_error(self, p):
        if p:
            raise ParsingException("invalid token '%s' at (%s, %d)" % (p.value, p.lineno, p.lexpos))
        else:
            raise ParsingException("unknown error")


def load_metamodel(filenames):
    '''
    Load and return a meta model from a list of filenames.
    '''
    loader = ModelLoader()
    loader.build_parser()
    for filename in filenames:
        loader.filename_input(filename)
    
    return loader.build_metamodel()

