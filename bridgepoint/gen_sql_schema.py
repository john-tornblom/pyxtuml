#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Generate an sql schema file for an xtUML model. 
The arguments are either xtuml files, or folders containing *.xtuml files.
Note that some type of attributes are not supported, e.g. instance handles or timers.
'''

import sys
import optparse
import logging

import xtuml
from xtuml import navigate_one as one
from xtuml import navigate_many as many

from . import ooaofooa


logger = logging.getLogger('gen_sql_schema')


def subtype(inst, relid, *kinds):
    '''
    Navigate a list of BridgePoint sub types and return the first non-empty hit.
    '''
    for kind in kinds:
        child = one(inst).nav(kind, relid)()
        if child: 
            return child


def mult_cond(mult, cond):
    '''
    Create the cardinality string used on xtuml associations.
    '''
    if mult:
        s = 'M'
    else:
        s = '1'
    if cond:
        s += 'C'
        
    return s


def get_data_type_name(s_dt):
    '''
    Convert a BridgePoint data type to a pyxtuml meta model type.
    '''
    s_cdt = one(s_dt).S_CDT[17]()
    if s_cdt and s_cdt.core_typ in range(1, 6):
        return s_dt.name
    
    if one(s_dt).S_EDT[17]():
        return 'INTEGER'
    
    s_dt = one(s_dt).S_UDT[17].S_DT[18]()
    if s_dt:
        return get_data_type_name(s_dt)
    

def get_attribute_type(o_attr):
    '''
    Get the pyxtuml meta model type associated with a Bridg3ePoint class attribute.
    '''
    ref_o_attr = one(o_attr).O_RATTR[106].O_BATTR[113].O_ATTR[106]()
    if ref_o_attr:
        return get_attribute_type(ref_o_attr)
    else:
        s_dt = one(o_attr).S_DT[114]()
        return get_data_type_name(s_dt)
 
    
def get_related_attributes(r_rgo, r_rto):
    '''
    The two lists of attributes which relates two classes in an association.
    '''
    l1 = list()
    l2 = list()
    
    ref_filter = lambda ref: ref.OIR_ID == r_rgo.OIR_ID
    for o_ref in many(r_rto).O_RTIDA[110].O_REF[111](ref_filter):
        o_attr = one(o_ref).O_RATTR[108].O_ATTR[106]()
        l1.append(o_attr.Name)
            
    for o_attr in many(r_rto).O_ID[109].O_OIDA[105].O_ATTR[105]():
        l2.append(o_attr.Name)
        
    return l1, l2

            
def mk_class(m, o_obj):
    '''
    Create a pyxtuml class from a BridgePoint class.
    '''
    first_filter = lambda selected: not one(selected).O_ATTR[103, 'precedes']()
    o_attr = xtuml.navigate_any(o_obj).O_ATTR[102](first_filter)
    attributes = list()
        
    while o_attr:
        ty = get_attribute_type(o_attr)
        if ty and not one(o_attr).O_BATTR[106].O_DBATTR[107]():
            attributes.append((o_attr.Name, ty))
        else:
            logger.warning('Omitting unsupported attribute %s.%s ' % (o_obj.Key_Lett, o_attr.Name))
            
        o_attr = one(o_attr).O_ATTR[103, 'succeeds']()
            
    return m.define_class(o_obj.Key_Lett, list(attributes), o_obj.Descrip)


def mk_simple_association(m, inst):
    '''
    Create a pyxtuml association from a simple association in BridgePoint.
    '''
    r_rel = one(inst).R_REL[206]()

    r_form = one(inst).R_FORM[208]()
    r_part = one(inst).R_PART[207]()
    
    if None in [r_form, r_part]:
        logger.info('Omitting unformalized association R%s' % (r_rel.Numb))
        return
    
    r_rgo = one(r_form).R_RGO[205]()
    r_rto = one(r_part).R_RTO[204]()
    
    source_o_obj = one(r_rgo).R_OIR[203].O_OBJ[201]()
    target_o_obj = one(r_rto).R_OIR[203].O_OBJ[201]()
    
    source_cardinality = mult_cond(r_form.Mult, r_form.Cond)
    target_cardinality = mult_cond(r_part.Mult, r_part.Cond)
    
    source_ids, target_ids = get_related_attributes(r_rgo, r_rto)
    
    source = xtuml.AssociationLink(source_o_obj.Key_Lett, source_cardinality,
                                   source_ids, r_part.Txt_Phrs)

    target = xtuml.AssociationLink(target_o_obj.Key_Lett, target_cardinality,
                                   target_ids, r_form.Txt_Phrs)
    
    if target.kind != source.kind:
        target.phrase = source.phrase = ''
        
    m.define_association(r_rel.Numb, source, target)


def mk_linked_association(m, inst):
    '''
    Create pyxtuml associations from a linked association in BridgePoint.
    '''
    r_rel = one(inst).R_REL[206]()
    r_rgo = one(inst).R_ASSR[211].R_RGO[205]()
    source_o_obj = one(r_rgo).R_OIR[203].O_OBJ[201]()
    
    def _mk_link(side1, side2):
        r_rto = one(side1).R_RTO[204]()

        target_o_obj = one(r_rto).R_OIR[203].O_OBJ[201]()
        cardinality = mult_cond(side2.Mult, side2.Cond)
        source_ids, target_ids = get_related_attributes(r_rgo, r_rto)
    
        source = xtuml.AssociationLink(source_o_obj.Key_Lett, cardinality, source_ids, side1.Txt_Phrs)
        target = xtuml.AssociationLink(target_o_obj.Key_Lett, '1', target_ids, side2.Txt_Phrs)

        if side1.Obj_ID != side2.Obj_ID:
            target.phrase = source.phrase = ''
        
        m.define_association(r_rel.Numb, source, target)
        
    r_aone = one(inst).R_AONE[209]()
    r_aoth = one(inst).R_AOTH[210]()
    
    if None in [r_rgo, r_aone, r_aoth]:
        logger.info('Omitting unformalized association R%s' % (r_rel.Numb))
        return
    
    _mk_link(r_aone, r_aoth)
    _mk_link(r_aoth, r_aone)
  
    
def mk_subsuper_association(m, inst):
    '''
    Create pyxtuml associations from a sub/super association in BridgePoint.
    '''
    r_rel = one(inst).R_REL[206]()
    r_rto = one(inst).R_SUPER[212].R_RTO[204]()
    target_o_obj = one(r_rto).R_OIR[203].O_OBJ[201]()
    
    if not r_rto:
        logger.info('Omitting unformalized association R%s' % (r_rel.Numb))
        return
    
    for r_sub in many(inst).R_SUB[213]():
        r_rgo = one(r_sub).R_RGO[205]()

        source_o_obj = one(r_rgo).R_OIR[203].O_OBJ[201]()
        source_ids, target_ids = get_related_attributes(r_rgo, r_rto)
        
        source = xtuml.AssociationLink(source_o_obj.Key_Lett, '1C', source_ids)
        target = xtuml.AssociationLink(target_o_obj.Key_Lett, '1', target_ids)
        
        m.define_association(r_rel.Numb, source, target)


def mk_derived_association(m, inst):
    '''
    Create a pyxtuml association from a derived association in BridgePoint.
    '''
    pass


def mk_association(m, r_rel):
    handler = {
               'R_SIMP': mk_simple_association,
               'R_ASSOC': mk_linked_association,
               'R_SUBSUP': mk_subsuper_association,
               'R_COMP': mk_derived_association,
    }
    inst = subtype(r_rel, 206, *handler.keys())
    fn = handler[inst.__class__.__name__]
    return fn(m, inst)


def mk_metamodel(bp_model, c_c=None):
    '''
    Create a pyxtuml meta model from a BridgePoint model. 
    Optionally, restrict to classes and associations contained in the component c_c.
    '''
    target = xtuml.MetaModel()

    c_c_filt = lambda sel: c_c is None or ooaofooa.is_contained_in(sel, c_c)
    
    for o_obj in bp_model.select_many('O_OBJ', c_c_filt):
        mk_class(target, o_obj)
        
    for r_rel in bp_model.select_many('R_REL', c_c_filt):
        mk_association(target, r_rel)
        
    return target


def main():
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

    loader = ooaofooa.Loader()
    for filename in args:
        loader.filename_input(filename)
        
    source = loader.build_metamodel(ignore_undefined_classes=True)
    c_c = source.select_any('C_C', lambda inst: inst.Name == opts.component)
    if not c_c and opts.component:
        logger.error('unable to find a component named %s' % opts.component)
        logger.info('available components to choose from are: %s' % ', '.join([c_c.Name for c_c in source.select_many('C_C')]))
        sys.exit(1)

    target = mk_metamodel(source, c_c)
        
    xtuml.persist_schema(target, opts.output)

    
if __name__ == '__main__':
    main()
    
    
