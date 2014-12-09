header {
import xtuml.model
import statement
}

options {
    language = Python;
}

class SqlParser extends Parser;
options {
	exportVocab=Sql;
    defaultErrorHandler = true;
    k=2;
}

sql_file returns [statements]
{statements = list()}
    :
    (
      stmt = statement { statements.append(stmt) }
    )+
    EOF
    ;

statement returns [stmt]
    : stmt = insert_statement
    | stmt = create_statement
    | stmt = relate_statement
    ;

insert_statement returns [stmt]
    :
    "insert"
    "into"
    kind = ident        { stmt = statement.InsertStmt(kind) }
    "values"
    TOK_LPAREN
    val = data_value    { stmt.values.append(val) }
    (
      TOK_COMMA
      val = data_value  { stmt.values.append(val) }
    )*
    TOK_RPAREN
    Semicolon
    ;

create_statement returns [stmt]
    :
    "create"
    "table"
    kind = ident       { stmt = statement.CreateStmt(kind) }
    TOK_LPAREN
    attr = attribute   { stmt.attributes.append(attr) }
    (
      TOK_COMMA
      attr = attribute { stmt.attributes.append(attr) }
    )*
    TOK_RPAREN
    Semicolon
    ;

relate_statement returns [stmt]
    :
    "create"
    "rop"
    "ref_id"
    id_ = ref_id          { stmt = statement.RelateStmt(id_) }
    "from"
    ass = association_end { stmt.end_points.append(ass) }
    "to"
    ass = association_end { stmt.end_points.append(ass) }
    Semicolon
    ;

association_end returns [ep]
    :
    c = cardinality
    kind = ident  { ep = xtuml.model.EndPoint(kind, c) }
    TOK_LPAREN
    id_ = ident   { ep.ids.append(id_) }
    (
      TOK_COMMA
      id_ = ident { ep.ids.append(id_) }
    )*
    TOK_RPAREN
    (
      ph = phrase { ep.phrase = ph }
    )?
    ;

cardinality returns [s]
{ s = self.LT(1).text }
    : (TOK_ID | TOK_NUMBER)
      (
        { s += self.LT(1).text }
        TOK_ID
      )?
    ;

attribute returns [attr]
    : name = ident 
      kind = ident
    { attr = xtuml.model.Attribute(name, kind.lower()) }
    ;

ref_id returns [s]
{ s = self.LT(1).text }
    : TOK_ID
    ;

data_value returns [s]
{ s = self.LT(1).text }
    : TOK_STRING
    | TOK_NUMBER
    | TOK_UUID
    ;

phrase returns [s]
{ s = self.LT(2).text }
    :
    "phrase"
    TOK_STRING
    ;

ident returns [s]
{ s = self.LT(1).text }
    : "phrase"
    | "to"
    | "from"
    | "ref_id"
    | "rop"
    | "table"
    | "values"
    | "into"
    | "insert"
    | "create"
    | TOK_ID
    ;
