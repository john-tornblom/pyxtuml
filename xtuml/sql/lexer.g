options {
    language=Python;
}

class SqlLexer extends Lexer;
options {
	importVocab=Sql;
    caseSensitiveLiterals=false;
    caseSensitive=false;
    testLiterals=true;
    k=2;
    charVocabulary = '\u0000'..'\ufffe';
}


TOK_ID
  :
  ( 'a'..'z'
  | '_'
  )
  ( 'a'..'z'
  | '_'
  | '0'..'9'
  )*
  ;
TOK_NUMBER
  :
  ('-')?
  ( '0'..'9'
  | '.'
  )+
  ;
TOK_STRING
  :
  '\''
  (
     "''"
   | '\r'!
   | '\n' { self.newline(); }
   | ~('\r' | '\'' | '\n')
  )*
  '\''
  ;
TOK_UUID
  :
  '"'!
  ( '0'..'9'
  | 'a'..'f'
  | '-'
  )*
  '"'!
  ;
SL_COMMENT
  :
  "--"
  (~'\n')*
  ('\n' { self.newline(); } )
    { $setType(Token.SKIP) }
  ;

WS
  : (WS1 | WS2)+
	{ $setType(Token.SKIP) }
  ;
protected
WS1
  : ( ' ' | '\t' )
  ;
protected
WS2
  :
  ( ("\r\n")=>"\r\n"
  | '\n'
  | '\r'
  ) { self.newline() }
  ;

TOK_COMMA  : ',';
TOK_LPAREN : '(';
TOK_RPAREN : ')';
Semicolon  : ';';

