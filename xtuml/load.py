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
        'PHRASE',
        'TRUE',
        'FALSE'
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

    def populate_classes(self, m):
        '''
        Populate a metamodel with classes previously encountered from input
        '''
        for stmt in self.statements:
            if isinstance(stmt, CreateClassStmt):
                m.define_class(stmt.kind, stmt.attributes)

    def populate_associations(self, m):
        '''
        Populate a metamodel with associations previously encountered from input
        '''
        for stmt in self.statements:
            if isinstance(stmt, CreateRelatationStmt):
                m.define_relation(stmt.id, *stmt.end_points)
                
    @staticmethod
    def deserialize_value(ty, value):
        '''
        Obtain the default value for a named meta model type.
        '''
        uty = ty.upper()
        
        if uty == 'BOOLEAN':
            if value.isdigit():
                return bool(int(value))
            elif value.upper() == 'FALSE':
                return False
            elif value.upper() == 'TRUE':
                return True
            else:
                raise ParsingException("Unable to convert '%s' to a boolean" % value)
            
        elif uty == 'INTEGER': 
            return int(value)
        
        elif uty == 'REAL': 
            return float(value)
        
        elif uty == 'STRING': 
            return value.replace("''", "'")[1:-1]
        
        elif uty == 'UNIQUE_ID': 
            if '"' in value:
                return uuid.UUID(value[1:-1]).int
            else:
                return int(value)
        
        else:
            raise ParsingException("Unknown type named '%s'" % ty)
        
    def populate_instances(self, m):
        '''
        Populate a metamodel with classes previously encountered from input
        '''
        for stmt in self.statements:
            if isinstance(stmt, CreateInstanceStmt):
                Cls = m.classes[stmt.kind]
                args = list()
                
                for attr, value in zip(Cls.__a__, stmt.values):
                    _, ty = attr
                    value = self.deserialize_value(ty, value) 
                    args.append(value)
            
                m.new(stmt.kind, *args)

    def populate(self, m):
        '''
        Populate a metamodel with entities previously encountered from input
        '''
        self.populate_classes(m)
        self.populate_associations(m)
        self.populate_instances(m)
        
    def build_metamodel(self, id_generator=None, ignore_undefined_classes=False):
        '''
        Build and return a meta model from previously parsed input.
        '''
        m = model.MetaModel(id_generator)
        m.ignore_undefined_classes = ignore_undefined_classes
        
        self.populate(m)
        
        return m

    def t_comment(self, t):
        r'\-\-([^\n]*\n?)'
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
        vup = t.value.upper()
        if vup in self.reserved:
            t.type = vup
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

    def p_empty_translation_unit(self, p):
        '''translation_unit :'''
        p[0] = list()
        
    def p_translation_unit(self, p):
        '''translation_unit : statement_sequence'''
        p[0] = p[1]

    def p_statement_sequence(self, p):
        '''statement_sequence : statement_sequence statement'''
        p[0] = p[1]
        p[0].append(p[2])

    def p_statement_sequence_endpoint(self, p):
        '''statement_sequence : statement'''
        p[0] = [p[1]]
        
    def p_statement(self, p):
        '''
        statement : create_table_statement SEMICOLON
                  | insert_into_statement SEMICOLON
                  | create_rop_statement SEMICOLON
                  
        '''
        p[0] = p[1]

    def p_create_table_statement(self, p):
        '''create_table_statement : CREATE TABLE identifier LPAREN attribute_sequence RPAREN'''
        p[0] = CreateClassStmt(p[3], p[5])

    def p_empty_attribute_sequence(self, p):
        '''attribute_sequence : '''
        p[0] = []
        
    def p_attribute_sequence_endpoint(self, p):
        '''attribute_sequence : attribute'''
        p[0] = [p[1]]

    def p_attribute_sequence(self, p):
        '''attribute_sequence : attribute_sequence COMMA attribute'''
        p[0] = p[1]
        p[0].append(p[3])

    def p_attribute(self, p):
        '''attribute : identifier identifier'''
        p[0] = (p[1], p[2])

    def p_insert_into_statement(self, p):
        '''
        insert_into_statement : INSERT INTO identifier VALUES LPAREN value_sequence RPAREN
        '''
        p[0] = CreateInstanceStmt(p[3], p[6])

    def p_empty_value_sequence(self, p):
        '''value_sequence : '''
        p[0] = []

    def p_value_sequence(self, p):
        '''value_sequence : value_sequence COMMA value'''
        p[0] = p[1]
        p[0].append(p[3])
        
    def p_value_sequence_endpoint(self, p):
        '''value_sequence : value'''
        p[0] = [p[1]]
        
    def p_value(self, p):
        '''
        value : FRACTION
              | NUMBER
              | STRING
              | GUID
              | TRUE
              | FALSE
        '''
        p[0] = p[1]

    def p_negative_value(self, p):
        '''
        value : MINUS FRACTION
              | MINUS NUMBER
        '''
        p[0] = p[1] + p[2]
        
    def p_create_rop_statement(self, p):
        '''create_rop_statement : CREATE ROP REF_ID RELID FROM association_end TO association_end'''
        p[0] = CreateRelatationStmt(p[6], p[8], p[4])

    def p_association_end(self, p):
        '''association_end : cardinality identifier LPAREN identifier_sequence RPAREN'''
        p[0] = model.AssociationLink(p[2], p[1], p[4])

    def p_phrased_association_end(self, p):
        '''association_end : cardinality identifier LPAREN identifier_sequence RPAREN PHRASE STRING'''
        p[0] = model.AssociationLink(p[2], p[1], p[4], p[7][1:-1])

    def p_cardinality_1(self, p):
        '''cardinality : NUMBER'''
        if p[1] != '1':
            raise ParsingException("invalid cardinality '%s' at (%s, %d)" % (p[1], p.lineno(1), p.lexpos(1)))
        p[0] = p[1]

    def p_cardinality_many(self, p):
        '''cardinality : ID'''
        if p[1] not in ['M', 'MC']:
            raise ParsingException("invalid cardinality '%s' at (%s, %d)" % (p[1], p.lineno(1), p.lexpos(1)))
        p[0] = p[1]

    def p_cardinality_01(self, p):
        '''cardinality : CARDINALITY'''
        p[0] = p[1]

    def p_empty_identifier_sequence(self, p):
        '''identifier_sequence : '''
        p[0] = []
        
    def p_identifier_sequence(self, p):
        '''identifier_sequence : identifier_sequence COMMA identifier'''
        p[0] = p[1]
        p[0].append(p[3])

    def p_identifier_sequence_endpoint(self, p):
        '''identifier_sequence : identifier'''
        p[0] = [p[1]]

    def p_identifier(self, p):
        '''
        identifier : ID
                   | CREATE
                   | INSERT
                   | INTO
                   | VALUES
                   | TABLE
                   | ROP
                   | REF_ID
                   | FROM
                   | TO
                   | PHRASE
                   | TRUE
                   | FALSE
        '''
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

