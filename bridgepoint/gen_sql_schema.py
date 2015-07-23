#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Generate an sql schema file for an xtUML model. 
The arguments are either xtuml files, or folders containing *.xtuml files.
Note that some type of attributes are not supported, e.g. instance handles or timers.
'''

import os
import sys
import optparse
import logging


import xtuml.tools
from xtuml import navigate_one as one

logger = logging.getLogger('gen_sql_schema')


# parts of the meta model for BridgePoint (ooaofooa) which are used by this script
bp_schema = '''
CREATE TABLE PE_PE (Element_ID UNIQUE_ID,Visibility INTEGER,Package_ID UNIQUE_ID,Component_ID UNIQUE_ID,type INTEGER);
CREATE TABLE C_C (Id UNIQUE_ID,Package_ID UNIQUE_ID,NestedComponent_Id UNIQUE_ID,Name STRING,Descrip STRING,Mult INTEGER,Root_Package_ID UNIQUE_ID,isRealized BOOLEAN,Realized_Class_Path STRING);
CREATE TABLE EP_PKG (Package_ID UNIQUE_ID,Sys_ID UNIQUE_ID,Direct_Sys_ID UNIQUE_ID,Name STRING,Descrip STRING,Num_Rng INTEGER);
CREATE TABLE S_DT (DT_ID UNIQUE_ID,Dom_ID UNIQUE_ID,Name STRING,Descrip STRING,DefaultValue STRING);
CREATE TABLE S_CDT (DT_ID UNIQUE_ID,Core_Typ INTEGER);
CREATE TABLE S_EDT (DT_ID UNIQUE_ID);
CREATE TABLE S_UDT (DT_ID UNIQUE_ID,CDT_DT_ID UNIQUE_ID,Gen_Type INTEGER);
CREATE TABLE O_OBJ (Obj_ID UNIQUE_ID,Name STRING,Numb INTEGER,Key_Lett STRING,Descrip STRING,SS_ID UNIQUE_ID);
CREATE TABLE O_ATTR (Attr_ID UNIQUE_ID,Obj_ID UNIQUE_ID,PAttr_ID UNIQUE_ID,Name STRING,Descrip STRING,Prefix STRING,Root_Nam STRING,Pfx_Mode INTEGER,DT_ID UNIQUE_ID,Dimensions STRING,DefaultValue STRING);
CREATE TABLE O_RATTR (Attr_ID UNIQUE_ID,Obj_ID UNIQUE_ID,BAttr_ID UNIQUE_ID,BObj_ID UNIQUE_ID,Ref_Mode INTEGER,BaseAttrName STRING);
CREATE TABLE O_BATTR (Attr_ID UNIQUE_ID,Obj_ID UNIQUE_ID);
CREATE TABLE O_NBATTR (Attr_ID UNIQUE_ID,Obj_ID UNIQUE_ID);

CREATE ROP REF_ID R102 FROM MC O_ATTR (Obj_ID) TO 1 O_OBJ (Obj_ID);
CREATE ROP REF_ID R103 FROM 1C O_ATTR (PAttr_ID, Obj_ID) PHRASE 'succeeds' TO 1C O_ATTR (Attr_ID, Obj_ID) PHRASE 'precedes';
CREATE ROP REF_ID R113 FROM MC O_RATTR (BAttr_ID, BObj_ID) TO 1 O_BATTR (Attr_ID, Obj_ID);
CREATE ROP REF_ID R114 FROM MC O_ATTR (DT_ID) TO 1 S_DT (DT_ID);
CREATE ROP REF_ID R106 FROM 1C O_BATTR (Attr_ID, Obj_ID) TO 1 O_ATTR (Attr_ID, Obj_ID);
CREATE ROP REF_ID R106 FROM 1C O_RATTR (Attr_ID, Obj_ID) TO 1 O_ATTR (Attr_ID, Obj_ID);
CREATE ROP REF_ID R107 FROM 1C O_NBATTR (Attr_ID, Obj_ID) TO 1 O_BATTR (Attr_ID, Obj_ID);
CREATE ROP REF_ID R17  FROM 1C S_CDT (DT_ID) TO 1 S_DT (DT_ID);
CREATE ROP REF_ID R17  FROM 1C S_UDT (DT_ID) TO 1 S_DT (DT_ID);
CREATE ROP REF_ID R17  FROM 1C S_EDT (DT_ID) TO 1 S_DT (DT_ID);
CREATE ROP REF_ID R18  FROM MC S_UDT (CDT_DT_ID) TO 1 S_DT (DT_ID);
CREATE ROP REF_ID R8000 FROM MC PE_PE (Package_ID) TO 1C EP_PKG (Package_ID);
CREATE ROP REF_ID R8001 FROM 1C EP_PKG (Package_ID) TO 1 PE_PE (Element_ID);
CREATE ROP REF_ID R8001 FROM 1C C_C (Id) TO 1 PE_PE (Element_ID);
CREATE ROP REF_ID R8001 FROM 1C O_OBJ (Obj_ID) TO 1 PE_PE (Element_ID);
CREATE ROP REF_ID R8003 FROM MC PE_PE (Component_ID) TO 1C C_C (Id);
'''

# global data types used by BridgePoint.
bp_globals = '''
INSERT INTO S_CDT VALUES ("ba5eda7a-def5-0000-0000-000000000000", 0);
INSERT INTO PE_PE VALUES ("ba5eda7a-def5-0000-0000-000000000001", 1, "00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", 3);
INSERT INTO S_DT  VALUES ("ba5eda7a-def5-0000-0000-000000000001", "00000000-0000-0000-0000-000000000000", 'boolean', '', '');
INSERT INTO S_CDT VALUES ("ba5eda7a-def5-0000-0000-000000000001",1);
INSERT INTO PE_PE VALUES ("ba5eda7a-def5-0000-0000-000000000002",1,"00000000-0000-0000-0000-000000000000","00000000-0000-0000-0000-000000000000",3);
INSERT INTO S_DT  VALUES ("ba5eda7a-def5-0000-0000-000000000002","00000000-0000-0000-0000-000000000000",'integer','','');
INSERT INTO S_CDT VALUES ("ba5eda7a-def5-0000-0000-000000000002",2);
INSERT INTO PE_PE VALUES ("ba5eda7a-def5-0000-0000-000000000003",1,"00000000-0000-0000-0000-000000000000","00000000-0000-0000-0000-000000000000",3);
INSERT INTO S_DT  VALUES ("ba5eda7a-def5-0000-0000-000000000003","00000000-0000-0000-0000-000000000000",'real','','');
INSERT INTO S_CDT VALUES ("ba5eda7a-def5-0000-0000-000000000003",3);
INSERT INTO PE_PE VALUES ("ba5eda7a-def5-0000-0000-000000000004",1,"00000000-0000-0000-0000-000000000000","00000000-0000-0000-0000-000000000000",3);
INSERT INTO S_DT  VALUES ("ba5eda7a-def5-0000-0000-000000000004","00000000-0000-0000-0000-000000000000",'string','','');
INSERT INTO S_CDT VALUES ("ba5eda7a-def5-0000-0000-000000000004",4);
INSERT INTO PE_PE VALUES ("ba5eda7a-def5-0000-0000-000000000005",1,"00000000-0000-0000-0000-000000000000","00000000-0000-0000-0000-000000000000",3);
INSERT INTO S_DT  VALUES ("ba5eda7a-def5-0000-0000-000000000005","00000000-0000-0000-0000-000000000000",'unique_id','','');
INSERT INTO S_CDT VALUES ("ba5eda7a-def5-0000-0000-000000000005",5);
INSERT INTO PE_PE VALUES ("ba5eda7a-def5-0000-0000-000000000007",1,"00000000-0000-0000-0000-000000000000","00000000-0000-0000-0000-000000000000",3);
INSERT INTO S_DT  VALUES ("ba5eda7a-def5-0000-0000-000000000007","00000000-0000-0000-0000-000000000000",'same_as<Base_Attribute>','','');
INSERT INTO S_CDT VALUES ("ba5eda7a-def5-0000-0000-000000000007",7);
'''


def is_contained_in(pe_pe, root):
    '''
    Determine if a PE_PE is contained within a EP_PKG or a C_C.
    '''
    if not pe_pe:
        return False
    
    if pe_pe.__class__.__name__ != 'PE_PE':
        pe_pe = one(pe_pe).PE_PE[8001]()
    
    ep_pkg = one(pe_pe).EP_PKG[8000]()
    c_c = one(pe_pe).C_C[8003]()
    
    if root in [ep_pkg, c_c]:
        return True
    
    elif is_contained_in(ep_pkg, root):
        return True
    
    elif is_contained_in(c_c, root):
        return True
    
    else:
        return False


class BPModelTransformation(xtuml.tools.Walker):
    '''
    Transforms a BridgePoint xtUML model into an xtUML meta model.
    '''
    
    source = None
    target = None
    
    def __init__(self, source, target):
        self.source = source
        self.target = target
        xtuml.tools.Walker.__init__(self)
        
    def transform(self, c_c=None):
        filt = lambda sel: c_c is None or is_contained_in(sel, c_c)
        for o_obj in self.source.select_many('O_OBJ', filt):
            self.accept(o_obj)
        
    def accept_S_DT(self, inst):
        for kind in ['S_CDT', 'S_EDT', 'S_UDT']:
            child = one(inst).nav(kind, 17)()
            if child: 
                return self.accept(child)

    def accept_S_CDT(self, inst):
        s_dt = one(inst).S_DT[17]()
        if s_dt.Name in ['boolean', 'integer', 'real', 'string', 'unique_id']:
            return s_dt.Name
        
    def accept_S_EDT(self, inst):
        return 'integer'
        
    def accept_S_UDT(self, inst):
        return self.accept(one(inst).S_DT[18]())
        
    def accept_O_ATTR(self, inst):
        ref_o_attr = one(inst).O_RATTR[106].O_BATTR[113].O_ATTR[106]()
        if ref_o_attr:
            return self.accept(ref_o_attr)
        
        elif one(inst).O_BATTR[106].O_NBATTR[107]():
            return self.accept(one(inst).S_DT[114]())
    
        else:
            return self.accept(one(inst).S_DT[114]())

    def accept_O_OBJ(self, inst):
        first_filter = lambda selected: not one(selected).O_ATTR[103, 'precedes']()
        o_attr = xtuml.navigate_any(inst).O_ATTR[102](first_filter)
        attributes = list()
        
        while o_attr:
            ty = self.accept(o_attr)
            if ty:
                attributes.append((o_attr.Name, ty))
            else:
                logger.warning('Omitting %s.%s ' % (inst.Key_Lett, o_attr.Name))
                
            o_attr = one(o_attr).O_ATTR[103, 'succeeds']()
        self.target.define_class(inst.Key_Lett, iter(attributes))



def gen_schema():
    '''
    Parse argv for options and arguments, and start schema generation.
    '''
    parser = optparse.OptionParser(usage="%prog [options] arg ...", formatter=optparse.TitledHelpFormatter())
    parser.set_description(__doc__)
    parser.add_option("-c", "--component", dest="component", metavar="NAME", help="export sql schema for the component named NAME", action="store", default=None)
    parser.add_option("-o", "--output", dest='output', metavar="PATH", action="store", help="save sql schema to PATH (required)", default=None)
    
    (opts, args) = parser.parse_args()
    if len(args) == 0 or opts.output is None:
        parser.print_help()
        sys.exit(1)
        
    logging.basicConfig(level=logging.INFO)

    loader = xtuml.ModelLoader()
    loader.build_parser()
    loader.input(bp_schema)
    loader.input(bp_globals)
    
    for arg in args:
        if os.path.isdir(arg):
            for path, _, files in os.walk(arg):
                for name in files:
                    if name.endswith('.xtuml'):
                        loader.filename_input(os.path.join(path, name))
        else:
            loader.filename_input(arg)
    
    source = loader.build_metamodel(ignore_undefined_classes=True)
    target = xtuml.MetaModel()
    tr = BPModelTransformation(source, target)
    
    c_c = source.select_any('C_C', lambda inst: inst.Name == opts.component)
    if opts.component and not c_c:
        logger.error('unable to find a component named %s' % opts.component)
        logger.info('available components to choose from are: %s' % ', '.join([c_c.Name for c_c in source.select_many('C_C')]))
        sys.exit(1)
    else:
        tr.transform(c_c)
        
    xtuml.persist_schema(target, opts.output)

    
if __name__ == '__main__':
    gen_schema()

