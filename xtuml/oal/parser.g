header {
import ast	
}

options {
    language = Python;
}


class OalParser extends Parser;
options {
    exportVocab = Oal;
    defaultErrorHandler = false;
    k = 2;
}

action returns [node]
  :
    block = block[True] { node = ast.BodyNode(block) }
    EOF
  ;
block[isRoot] returns [node]
{node = ast.BlockNode()}
    :
        ( options {
                greedy = false;
                warnWhenFollowAmbig = false;
            }:
            child = statement {node.children.append(child)}
        )*
    ;

statement returns [node]
  :
  (
    (implicit_ib_transform_statement )=> node = implicit_ib_transform_statement
  | (function_statement )=> node = function_statement
  | node = implicit_assignment_statement
  | node = implicit_invocation_statement
  | node = assignment_statement
  | node = control_statement
  | node = break_statement
  | node = bridge_statement
  | node = send_statement
  | node = continue_statement
  | node = create_object_statement
  | node = create_event_statement
  | node = delete_statement
  | node = for_statement
  | node = generate_statement
  | node = if_statement
  | node = relate_statement
  | node = return_statement
  | node = select_statement
  | node = transform_statement
  | node = while_statement
  | node = unrelate_statement
  | node = debug_statement
  | node = empty_statement
  )
    Semicolon
  ;
assignment_statement returns [node]
  : "assign" node = assignment_expr
  ;
  
break_statement returns [node]
  : "break" {node = ast.BreakNode()}
  ;
  
bridge_statement returns [node]
  : "bridge"
    (
	    (
	      ( lval = member_access[True]     
	      | lval = param_data_access[True]
	      )
	      TOK_EQUAL
		    rval = bridge_invocation[True]
	    )
	    {node = ast.AssignmentNode(lval, rval)}
	|
	    node = bridge_invocation[False]
    )
  ;
 
send_statement returns [node]
  :
    "send"
    (
	    (
	      ( lval = member_access[True]     
	      | lval = param_data_access[True]
	      )
	      TOK_EQUAL
		    rval = message_invocation[True]
	    )
	    {node = ast.AssignmentNode(lval, rval)}
	|
	    node = message_invocation[False]
    )

  ;
control_statement returns [node]
  :
    "control"
    "stop"
  ;
continue_statement returns [node]
  :
    { node = ast.ContinueNode(self.LT(1)) }
    "continue"
  ;
create_event_statement returns [node]
  :
    "create"
    "event"
    "instance"
    var = local_variable[True]
    "of"
    evt = event_spec {node = ast.CreateEventNode(var, evt)}
  ;
create_object_statement returns [node]
{var = None}
  :
    "create"  
    "object"
    "instance"
  (
    (  local_variable[True] "of" )=> var = local_variable[True]
  )?
    "of"
    key_lett = object_keyletters {node = ast.CreateObjectNode(var, key_lett)}
  ;
debug_statement returns [node]
   :
     "_debug"  
     (
       ( debug_operand )+
     |
     )
  ;
delete_statement returns [node]
  :
    "delete"    
    "object"
    "instance"
    var = inst_ref_var {node = ast.DeleteNode(var)}
  ;
empty_statement returns [node]
  :
  ;
for_statement returns [node]
  :
    "for"   
    "each" var = local_variable[True] "in" set = inst_ref_set_var
      block = block[False]
    "end"  "for" {node = ast.ForEachNode(var, set, block)}
  ;
generate_statement returns [node]
  :
  "generate"  
  (
    var = event_spec
  |
    var = member_access[False]
  )
  {node = ast.GenerateNode(var)}
  ;
if_statement returns [node]
  :
    "if"
    expr = expr
      block = block[False] {node = ast.IfNode(expr, block)}
    (
      (
        "elif"
        expr = expr
      block = block[False] {node.elifs.append(ast.ElIfNode(expr, block))}
      )+
    )?
    (
      "else" 
      block = block[False] {node.iffalse = block}
    )?
    "end" "if"
  ;
implicit_assignment_statement returns [node]
  :
    node = assignment_expr
  ;
implicit_invocation_statement returns [node]
  :
  node = invocation[False]
  ;
implicit_ib_transform_statement returns [node]
  :
    node = transform_ib_invocation[False]
  ;
relate_statement returns [node]
{phrase = using = None}
  :
    "relate"   
    from_ = inst_ref_var
    "to"
    to = inst_ref_var
    "across"
    across = relationship
    (
      TOK_DOT
      phrase = phrase
    )?
    (
      "using"
      using = assoc_obj_inst_ref_var
    )?
    {node = ast.RelateNode(from_, to, across, phrase, using)}
    ;
return_statement returns [node]
{expr = None}
  :
    "return"   
  (
    expr = expr
  )?
  {node = ast.ReturnNode(expr)}
  ;
select_statement returns [node]
  :
    "select" {ty = self.LT(1).text}
    (
      "one"
      var = local_variable[True]
      spec = object_spec
    |
      "any"
      var = local_variable[True]
      spec = object_spec
    |
      "many"
      var = local_variable[True]
      spec = object_spec
    )
     {node = ast.SelectNode(var, spec, ty)}
    ;
transform_statement returns [node]
  :
    "transform"
    (
	    (
	      ( var = member_access[True] 
	      | var = param_data_access[True]
	      )
	      TOK_EQUAL
		    expr = transform_invocation[True] {node = ast.AssignmentNode(var, expr)}
	    )
	|
	    node = transform_invocation[False]
    )

  ;
function_statement returns [node]
  :
  TOK_DOUBLECOLON   
  node = function_invocation[False]
  ;
unrelate_statement returns [node]
{phrase = using = None}
  :
    "unrelate"   
    var1 = inst_ref_var
    "from"
    var2 = inst_ref_var
    "across"
    rel = relationship
    (
      TOK_DOT
      phrase = phrase
    )?
    (
      "using"
      using = assoc_obj_inst_ref_var
    )?
    { node = ast.UnrelateNode(var1, var2, rel, phrase, using) }
  ;
while_statement returns [node]
  :
    "while"    
      expr = expr
      block = block[False] { node = ast.WhileNode(expr, block) }
    "end" "while"
  ;
assignment_expr returns [node]
  :
  (
    lval = member_access[True]   
    TOK_EQUAL
    rval = expr
  |
    ( "param" TOK_DOT )=>
    lval = param_data_access[True]
    TOK_EQUAL
    rval = expr
  )
  { node = ast.AssignmentNode(lval, rval) }
  ;
bridge_invocation[isRval] returns [node]
{ args = None }
  :
    key_lett = ee_keyletters
    TOK_DOUBLECOLON
    fn = bridge_function
    TOK_LPAREN
    (
      args = invocation_parameters
    )?
    TOK_RPAREN
    { node = ast.BridgeInvocationNode(key_lett, fn, args) }
  ;
message_invocation[isRval] returns [node]
{ args = to = None }
  :
    ns = interface_or_port_name
    TOK_DOUBLECOLON
    fn = message_name
    TOK_LPAREN
    (
      args = invocation_parameters
    )?
    TOK_RPAREN
    (
      "to" 
      (
        to = rval
      )
    )?
    { node = ast.MessageInvocationNode(ns, fn, args, to) }
  ;
invocation[isRval] returns [node]
{ args = None }
  :
    ns = identifier
    TOK_DOUBLECOLON
    fn = invocation_function
    TOK_LPAREN
    (
      args = invocation_parameters
    )?
    TOK_RPAREN
    { node = ast.InvocationNode(ns, fn, args) }
  ;
bridge_expr returns [node]
  :
  "bridge"
  node = bridge_invocation[True]
  ;
invocation_expr returns [node]
  :
    node = invocation[True]
  ;
enumerator_access returns [node]
   :
    ty = enum_data_type
    TOK_DOUBLECOLON
    name = enumerator { node = ast.EnumAccessNode(ty, name) }
  ;
debug_operand
  :
    ( "_trace"
      (  "_off"
      |  "_on"
      )
    )
  | ( "_dump"
      (  "_off"
      |  "_on"
      )
    )
  | ( "_sor"
      (  "_off"
      |  "_on"
      )
    )
  | "_on"
  | "_off"
  | "_stat"
  ;
event_spec returns [node]
{ meaning = data = None }
  :
    lbl = event_label
    (
      TOK_TIMES
    )?
    (
      TOK_COLON
      meaning = event_meaning
    )?
    (
      TOK_LPAREN
      (
        data = supp_data
      )?
      TOK_RPAREN
    )?
    "to"
    (
      (
        ( object_keyletters ( "assigner" | "class" ) )=> to = object_keyletters ( "assigner" | "class" )
      |
        to = object_keyletters "creator"
      )
    |
      (
        to = inst_ref_var_or_ee_keyletters
      )
    )
    { node = ast.EventSpecNode(lbl, meaning, data, to) }
  ;
invocation_parameters returns [node]
{ node = ast.ParameterListNode() }
  :
    name = data_item[False]
    TOK_COLON
    value = expr { node.children.append(ast.ParameterNode(name, value)) }
    (
      TOK_COMMA
      name = data_item[False]
      TOK_COLON
      value = expr { node.children.append(ast.ParameterNode(name, value)) }
    )*
  ;
inst_ref_var_or_ee_keyletters returns [node]
  :
    (
      node = local_variable[False]
    | { node = ast.TerminalNode(self.LT(1)) }
      TOK_GENERAL_NAME
    |
      node = kw_as_id2
    )
  ;
interface_or_port_name returns [node]
  :
    node = general_name
  ;
message_name returns [node]
  :
    node = general_name
  ;
instance_chain returns [node]
{prev = None }
  :
    ( TOK_ARROW
      key_lett = object_keyletters
      TOK_LSQBR
      rel = relationship { phrase = None }
      (
        TOK_DOT
        phrase = phrase
      )?
      {node = ast.InstanceChainNode(key_lett, rel, phrase, prev) }
      { prev = node }
      TOK_RSQBR
    )+
  ;
object_spec returns [node]
  :
  (
    "related" "by"
    var = local_variable[False]
    chain = instance_chain
    { where = None }
    ( where = where_spec[True] )? { node = ast.NavigationNode(var, chain, where) }
  |
    "from" ( "instances" "of" )?
    key_lett = object_keyletters
    { where = None }
    ( where = where_spec[False] )? { node = ast.InstanceLookupNode(key_lett, where) }
  )
  ;
supp_data returns [node]
{ node = ast.ParameterListNode() }
  :
    name = supp_data_item
    TOK_COLON
    value = expr { node.children.append(ast.ParameterNode(name, value)) }
    (
      TOK_COMMA
      name = supp_data_item
      TOK_COLON
      value = expr { node.children.append(ast.ParameterNode(name, value)) }
    )*
  ;
  
  
function_invocation[isRval] returns [node]
  :
    fn = function_function
    { args = None }
    TOK_LPAREN
    (
      args = invocation_parameters
    )?
    { node = ast.FunctionInvocationNode(fn, args) }
    TOK_RPAREN
  ;
transform_ib_invocation[isRval] returns [node]
  :
    var = inst_ref_var
    TOK_DOT
    fn = transformer_function[False]
    TOK_LPAREN
    { args = None }
    (
      args = invocation_parameters
    )?
    { node = ast.TransformerInvocationNode(var, fn, args) }
    TOK_RPAREN
  ;
transform_invocation[isRval] returns [node]
  :
    key_lett = object_keyletters
    TOK_DOUBLECOLON
    fn = transformer_function[True]
    TOK_LPAREN
    (
      args = invocation_parameters
    )?
    { node = ast.TransformerInvocationNode(key_lett, fn, args) }
    TOK_RPAREN
  ;
where_spec[isChain] returns [node]
  :
  "where" node = expr
  ;
assoc_obj_inst_ref_var returns [node]
  :
    node = inst_ref_var
  ;
bridge_function returns [node]
  :
    node = function_name
  ;
invocation_function returns [node]
  :
    node = function_name
  ;
data_item[isAccess] returns [node]
  :
    node = data_item_name
  ;
data_item_name returns [node]
  :
    node = general_name
  ;
enum_data_type returns [node]
  :
    node = general_name
  ;
enumerator returns [node]
  :
    node = general_name
  ;
keyletters returns [node]
  :
    node = general_name
  ;
ee_keyletters returns [node]
  :
    node = keyletters
  ;
event_label returns [node]
  :
    node = general_name
  ;
event_meaning returns [node]
  :
  (
    node = phrase
  )
  ;
general_name returns [node]
  :
  (
    node = limited_name
  | { node = ast.TerminalNode(self.LT(1)) }
    TOK_GENERAL_NAME
  |
    node = kw_as_id1
  |
    node = kw_as_id2
  |
    node = kw_as_id3
  )
  ;
svc_general_name returns [node]
  :
  (
    node = limited_name
  | { node = ast.TerminalNode(self.LT(1)) }
    TOK_GENERAL_NAME
  |
    node = kw_as_id1
  |
    node = kw_as_id2
  |
    node = kw_as_id3
  |
    node = kw_as_id4
  )
  ;
limited_name returns [node]
{ node = ast.TerminalNode(self.LT(1)) }
  :
    TOK_ID    
  |
    TOK_RELID
  ;
inst_ref_set_var returns [node]
  :
  node = local_variable[False]
  ;
inst_ref_var returns [node]
  :
  node = local_variable[False]
  ;
kw_as_id1 returns [node]
{ node = ast.TerminalNode(self.LT(1)) }
  :
  ( "across"
  | "any"
  | "assigner"
  | "assign"
  | "break"
  | "by"
  | "class"
  | "continue"
  | "control"
  | "create"
  | "creator"
  | "delete"
  | "each"
  | "end"
  | "event"
  | "for"
  | "from"
  | "generate"
  | "in"
  | "instances"
  | "instance"
  | "many"
  | "object"
  | "of"
  | "one"
  | "related"
  | "relate"
  | "select"
  | "stop"
  | "to"
  | "where"
  | "unrelate"
  | "using"
  )
  ;
kw_as_id2 returns [node]
{ node = ast.TerminalNode(self.LT(1)) }
  :
  ( "bridge"
  | "send"
  | "cardinality"
  | "empty"
  | "false"
  | "not"
  | "not_empty"
  | "transform"
  | "true"
  )
  ;
kw_as_id3 returns [node]
{ node = ast.TerminalNode(self.LT(1)) }
  :
  ( "param"
  | "rcvd_evt"
  | "selected"
  | "self"
  )
  ;
kw_as_id4 returns [node]
{ node = ast.TerminalNode(self.LT(1)) }
  :
  ( "and"
  | "elif"
  | "else"
  | "if"
  | "or"
  | "return"
  | "while"
  )
  ;
local_variable[isLval] returns [node]
  :
  lbl = root_element_label[isLval] { node = ast.LocalVariableNode(lbl) }
  ;
root_element_label[isLval] returns [node]
  :
  ( { node = ast.TerminalNode(self.LT(1)) }
    "selected" 
  | { node = ast.TerminalNode(self.LT(1)) }
    "self"     
  | node = limited_name
  | node = kw_as_id1
  )
  ;
element_label[isLval] returns [node]
  : node = general_name
  ;
function_name returns [node]
  : node = general_name
  ;
svc_function_name returns [node]
  : node = svc_general_name
  ;
identifier returns [node]
  : node = general_name
  ;
object_keyletters returns [node]
  : node = keyletters
  ;
phrase returns [node]
  :
  ( { node = ast.TerminalNode(self.LT(1)) }
    TICKED_PHRASE
  | node = svc_general_name
  )
  ;
relationship returns [node]
{ node = ast.TerminalNode(self.LT(1)) }
  : TOK_RELID
  ;
supp_data_item returns [node]
  : node = data_item_name
  ;
function_function returns [node]
  : node = svc_function_name
  ;
transformer_function[isKeyLett] returns [node]
  : node = function_name
  ;
expr returns [node]
  : node = sub_expr
  ;
sub_expr returns [node]
  :
    node = conjunction
    ( { op = ast.TerminalNode(self.LT(1)) }
      "or"
      rhs = conjunction { node = ast.BinaryOperationNode(node, op, rhs)}
    )*
  ;
conjunction returns [node]
  :
    node = relational_expr
    ( { op = ast.TerminalNode(self.LT(1)) }
      "and"
      rhs = relational_expr { node = ast.BinaryOperationNode(node, op, rhs)}
    )*
  ;
relational_expr returns [node]
  :
    node = addition
    (
      op = comparison_operator
      rhs = addition  { node = ast.BinaryOperationNode(node, op, rhs)}
    )?
  ;
addition returns [node]
  :
    node = multiplication
    (
      op = plus_or_minus
      rhs = multiplication  { node = ast.BinaryOperationNode(node, op, rhs)}
    )*
  ;
multiplication returns [node]
  :
    ( boolean_negation )=> node = boolean_negation
  |
    node = sign_expr
    (
      op = mult_op
      rhs = sign_expr { node = ast.BinaryOperationNode(node, op, rhs)}
    )*
  ;
sign_expr returns [node]
{ op = None }
  :
    (
      op = plus_or_minus
    )?
    node = term { if op: node = ast.UnaryOperationNode(node, op)}
  ;
boolean_negation returns [node]
  : { op = ast.TerminalNode(self.LT(1)) }
    "not"
    operand = term { node = ast.UnaryOperationNode(operand, op)}
  ;
term returns [node]
  :
	(cardinality_op) => node = cardinality_op
  |
    (empty_op) => node = empty_op
  |
    (not_empty_op) => node = not_empty_op
  |
    node = rval
  |
    TOK_LPAREN
    (
      ( assignment_expr )=> node = assignment_expr
    |
      node = expr
    )
    TOK_RPAREN
  ;
cardinality_op returns [node]
  : { op = ast.TerminalNode(self.LT(1)) }
    "cardinality" var = local_variable[False] { node = ast.UnaryOperationNode(var, op)}
  ;
empty_op returns [node]
  : { op = ast.TerminalNode(self.LT(1)) }
    "empty" var = local_variable[False]  { node = ast.UnaryOperationNode(var, op)}
  ;
not_empty_op returns [node]
  : { op = ast.TerminalNode(self.LT(1)) }
    "not_empty" var = local_variable[False] { node = ast.UnaryOperationNode(var, op)}
  ;
instance_start_segment[isLval] returns [node]
{ idx = None }
  :
    lbl = root_element_label[isLval]
    (
      idx = array_refs
    )?
    { node = ast.VariableAccessNode(lbl)}
    { if idx: node = ast.IndexedVariableAccessNode(node, idx) }
  ;
instance_access_segment[isLval] returns [node]
{ idx = None }
  :
    lbl = element_label[isLval]
    (
      idx = array_refs
    )?
    { node = ast.VariableAccessNode(lbl)}
    { if idx: node = ast.IndexedVariableAccessNode(node, idx) }
  ;
member_access[isLval] returns [node]
  :
  node = instance_start_segment[isLval]
  (TOK_DOT
   member = instance_access_segment[isLval] { node = ast.MemberAccessNode(node, member) }
  )*
  ;
param_data_access[isLval] returns [node]
  :
  "param"
  TOK_DOT
  member = member_access[isLval] { node = ast.ParamAccessNode(member) }
  ;
event_data_access returns [node]
  :
  "rcvd_evt"
  TOK_DOT
  member = member_access[False] { node = ast.EventAccessNode(member) }
  ;
array_refs returns [node]
{ node = ast.ArrayIndexListNode() }
  :
  (
    TOK_LSQBR
    index = expr { node.children.append(index) }
    TOK_RSQBR
  )+
  ;
rval returns [node]
  :
    ( TOK_DOUBLECOLON )=>
    TOK_DOUBLECOLON
    node = function_invocation[True]
  |
    ( transform_ib_invocation[True] )=>
    node = transform_ib_invocation[True]
  |
    ( invocation_expr )=>
    node = invocation_expr
  |
    ( enumerator_access )=>
    node = enumerator_access
  |
    node = member_access[False]
  |
    node = constant_value
  |
    ("rcvd_evt" TOK_DOT) =>
    node = event_data_access
  |
    node = bridge_expr
  |
    ("param" TOK_DOT) =>
    node = param_data_access[False]
  | { node = ast.TerminalNode(self.LT(1)) }
    TOK_QMARK
  ;
constant_value returns [node]
{ node = ast.TerminalNode(self.LT(1)) }
  : { node = ast.RealNode(self.LT(1))}
    TOK_FRACTION
  | { node = ast.IntegerNode(self.LT(1))}
    TOK_NUMBER
  | { node = ast.StringNode(self.LT(1))}
    TOK_STRING
  | { node = ast.BooleanNode(self.LT(1))}
    "true"
  | { node = ast.BooleanNode(self.LT(1))}
    "false"
  ;
comparison_operator returns [node]
{ node = ast.TerminalNode(self.LT(1)) }
  :
    TOK_DOUBLEEQUAL
  |
    TOK_NOTEQUAL
  |
    TOK_LESSTHAN
  |
    TOK_LE
  |
    TOK_GT
  |
    TOK_GE
  ;
plus_or_minus returns [node]
{ node = ast.TerminalNode(self.LT(1)) }
  :
    TOK_PLUS
  |
    TOK_MINUS
  ;
mult_op returns [node]
{ node = ast.TerminalNode(self.LT(1)) }
  :
    TOK_TIMES
  |
    TOK_DIV
  |
    TOK_MOD
  ;

