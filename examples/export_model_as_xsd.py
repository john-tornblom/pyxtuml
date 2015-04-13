#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import sys
import os

import xml.etree.ElementTree as ET
import xml.dom.minidom

base_dir = '%s/..' % os.path.dirname(__file__)
sys.path.append(base_dir)

from xtuml import io


def get_type_name(m, o_attr):
    s_dt = m.navigate_one(o_attr).S_DT[114]()
    while m.navigate_one(s_dt).S_UDT[17]():
        s_dt = m.navigate_one(s_dt).S_UDT[17].S_DT[18]()
        
    if   s_dt.name == 'string': return 'string'
    elif s_dt.name == 'integer': return 'integer'
    elif s_dt.name == 'real': return 'decimal'
    elif s_dt.name == 'boolean': return 'boolean'
    elif s_dt.name == 'unique_id': return 'integer'
    
    s_edt = m.navigate_one(s_dt).S_EDT[17]()
    if s_edt:
        return s_edt.name

    o_attr = m.navigate_one(o_attr).O_RATTR[106].O_BATTR[113].O_ATTR[106]()
    if o_attr:
        return get_type_name(m, o_attr)
    

def is_contained_in(m, pe_pe, root):
    if pe_pe.__class__.__name__ != 'PE_PE':
        pe_pe = m.navigate_one(pe_pe).PE_PE[8001]()

    c_c = m.navigate_one(pe_pe).C_C[8003]()
    if root == c_c:
        return True
    elif is_contained_in(m, pe_pe, c_c):
        return True
    
    ep_pkg = m.navigate_one(pe_pe).EP_PKG[8000]()
    if root == ep_pkg:
        return True
    elif is_contained_in(m, pe_pe, ep_pkg):
        return True
    
    return False


def is_global(m, pe_pe):
    if pe_pe.__class__.__name__ != 'PE_PE':
        pe_pe = m.navigate_one(pe_pe).PE_PE[8001]()

    if m.navigate_one(pe_pe).C_C[8003]():
        return False
       
    if m.navigate_one(pe_pe).EP_PKG[8000]():
        return False

    return True

    
def build_class(m, o_obj):
    cls = ET.Element('element', name=o_obj.key_lett, maxOccurs='unbounded')
    attributes = ET.SubElement(cls, 'complexType')
    for o_attr in m.navigate_many(o_obj).O_ATTR[102]():
        type_name = get_type_name(m, o_attr)
        if type_name:
            ET.SubElement(attributes, 'attribute', name=o_attr.name, type=type_name)

    return cls


def build_component(m, c_c):
    component = ET.Element('element', name=c_c.name)
    
    classes = ET.SubElement(component, 'complexType')
    classes = ET.SubElement(classes, 'sequence')
        
    scope_filter = lambda selected: is_contained_in(m, selected, c_c)
    for s_dt in m.select_many('S_DT', scope_filter):
        # TODO: data types
        pass
            
    for o_obj in m.select_many('O_OBJ', scope_filter):
        cls = build_class(m, o_obj)
        classes.append(cls)
    
    return component


def build_schema(m):
    schema = ET.Element('schema')
    schema.set('xmlns', 'http://www.w3.org/2001/XMLSchema')
    
    global_filter = lambda selected: is_global(m, selected)
    for s_dt in m.select_many('S_DT', global_filter):
        # TODO: data types
        pass
    
    for c_c in m.select_many('C_C'):
        component = build_component(m, c_c)
        schema.append(component)

    return schema


def prettify(xml_string):
    reparsed = xml.dom.minidom.parseString(xml_string)
    return reparsed.toprettyxml(indent="  ")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s <path to prebuild model.sql>' % sys.argv[0])
        sys.exit()
        
    loader = io.load.ModelLoader()
    loader.build_parser()
    loader.filename_input('%s/resources/ooaofooa_schema.sql' % base_dir)
    loader.filename_input(sys.argv[1])
    
    m = loader.build_metamodel()
    
    schema = build_schema(m)
    
    s = ET.tostring(schema, 'utf-8')
    s = prettify(s)
    
    print(s)

