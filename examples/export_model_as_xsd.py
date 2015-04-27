#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import sys
import os
import optparse
import logging

import xml.etree.ElementTree as ET
import xml.dom.minidom

base_dir = '%s/..' % os.path.dirname(__file__)
sys.path.append(base_dir)

from xtuml import io


logger = logging.getLogger('xsd_export')


def get_type_name(m, s_dt):
    '''
    get the xsd name of a S_DT
    '''
    s_cdt = m.navigate_one(s_dt).S_CDT[17]()
    if s_cdt and s_cdt.core_typ in range(1, 6):
        return s_dt.name
    
    s_edt = m.navigate_one(s_dt).S_EDT[17]()
    if s_edt:
        return s_dt.name
    
    s_udt = m.navigate_one(s_dt).S_UDT[17]()
    if s_udt:
        return s_dt.name

#    s_sdt = m.navigate_one(s_dt).S_SDT[17]()
#    if s_sdt:
#        return s_dt.name
    
    
def get_refered_attribute(m, o_attr):
    '''
    Get the the referred attribute.
    '''
    o_attr_ref = m.navigate_one(o_attr).O_RATTR[106].O_BATTR[113].O_ATTR[106]()
    if o_attr_ref:
        return get_refered_attribute(m, o_attr_ref)
    else:
        return o_attr
    
    
def is_contained_in(m, pe_pe, root):
    '''
    Determine if a PE_PE is contained within a EP_PKG or a C_C.
    '''
    if not pe_pe:
        return False
    
    if pe_pe.__class__.__name__ != 'PE_PE':
        pe_pe = m.navigate_one(pe_pe).PE_PE[8001]()
    
    ep_pkg = m.navigate_one(pe_pe).EP_PKG[8000]()
    c_c = m.navigate_one(pe_pe).C_C[8003]()
    
    if root in [ep_pkg, c_c]:
        return True
    
    elif is_contained_in(m, ep_pkg, root):
        return True
    
    elif is_contained_in(m, c_c, root):
        return True
    
    else:
        return False


def is_global(m, pe_pe):
    '''
    Check if a PE_PE is globally defined, i.e. not inside a C_C
    '''
    if pe_pe.__class__.__name__ != 'PE_PE':
        pe_pe = m.navigate_one(pe_pe).PE_PE[8001]()
    
    if m.navigate_one(pe_pe).C_C[8003]():
        return False
    
    pe_pe = m.navigate_one(pe_pe).EP_PKG[8000].PE_PE[8001]()
    if not pe_pe:
        return True
    
    return is_global(m, pe_pe)


def build_core_type(m, s_cdt):
    '''
    Build an xsd simpleType out of a S_CDT.
    '''
    s_dt = m.navigate_one(s_cdt).S_DT[17]()
    
    if s_dt.name == 'void':
        type_name = None
    
    elif s_dt.name == 'boolean':
        type_name = 'xs:boolean'
    
    elif s_dt.name == 'integer':
        type_name = 'xs:integer'
    
    elif s_dt.name == 'real':
        type_name = 'xs:decimal'
    
    elif s_dt.name == 'string':
        type_name = 'xs:string'
    
    elif s_dt.name == 'unique_id':
        type_name = 'xs:integer'
    
    else:
        type_name = None
    
    if type_name:
        mapped_type = ET.Element('xs:simpleType', name=s_dt.name)
        ET.SubElement(mapped_type, 'xs:restriction', base=type_name)
        return mapped_type


def build_enum_type(m, s_edt):
    '''
    Build an xsd simpleType out of a S_EDT.
    '''
    s_dt = m.navigate_one(s_edt).S_DT[17]()
    enum = ET.Element('xs:simpleType', name=s_dt.name)
    enum_list = ET.SubElement(enum, 'xs:restriction', base='xs:string')
    
    first_filter = lambda selected: not m.navigate_one(selected).S_ENUM[56, 'precedes']()
    
    s_enum = m.navigate_any(s_edt).S_ENUM[27](first_filter)
    while s_enum:
        ET.SubElement(enum_list, 'xs:enumeration', value=s_enum.name)
        s_enum = m.navigate_one(s_enum).S_ENUM[56, 'succeeds']()
    
    return enum


def build_struct_type(m, s_sdt):
    '''
    Build an xsd complexType out of a S_SDT.
    '''
    s_dt = m.navigate_one(s_sdt).S_DT[17]()
    struct = ET.Element('xs:complexType', name=s_dt.name)
    
    first_filter = lambda selected: not m.navigate_one(selected).S_MBR[46, 'precedes']()
    
    s_mbr = m.navigate_any(s_sdt).S_MBR[44](first_filter)
    while s_mbr:
        s_dt = m.navigate_one(s_mbr).S_DT[45]()
        type_name = get_type_name(m, s_dt)
        ET.SubElement(struct, 'xs:attribute', name=s_mbr.name, type=type_name)
        s_mbr = m.navigate_one(s_mbr).S_MBR[46, 'succeeds']()
    
    return struct


def build_user_type(m, s_udt):
    '''
    Build an xsd simpleType out of a S_UDT.
    '''
    s_dt_user = m.navigate_one(s_udt).S_DT[17]()
    s_dt_base = m.navigate_one(s_udt).S_DT[18]()
    
    base_name = get_type_name(m, s_dt_base)
    if base_name:
        user = ET.Element('xs:simpleType', name=s_dt_user.name)
        ET.SubElement(user, 'xs:restriction', base=base_name)
        
        return user


def build_type(m, s_dt):
    '''
    Build a partial xsd tree out of a S_DT and its sub types S_CDT, S_EDT, S_SDT and S_UDT.
    '''
    s_cdt = m.navigate_one(s_dt).S_CDT[17]()
    if s_cdt:
        return build_core_type(m, s_cdt)
    
    s_edt = m.navigate_one(s_dt).S_EDT[17]()
    if s_edt:
        return build_enum_type(m, s_edt)
    
    s_udt = m.navigate_one(s_dt).S_UDT[17]()
    if s_udt:
        return build_user_type(m, s_udt)
    
#    s_sdt = m.navigate_one(s_dt).S_SDT[17]()
#    if s_sdt:
#        return build_struct_type(m, s_sdt)


def build_class(m, o_obj):
    '''
    Build an xsd complex element out of a O_OBJ, including its O_ATTR.
    '''
    cls = ET.Element('xs:element', name=o_obj.key_lett, maxOccurs='unbounded')
    attributes = ET.SubElement(cls, 'xs:complexType')
    for o_attr in m.navigate_many(o_obj).O_ATTR[102]():
        o_attr_ref = get_refered_attribute(m, o_attr)
        s_dt = m.navigate_one(o_attr_ref).S_DT[114]()
        while m.navigate_one(s_dt).S_UDT[17]():
            s_dt = m.navigate_one(s_dt).S_UDT[17].S_DT[18]()
        
        type_name = get_type_name(m, s_dt)
        if type_name:
            ET.SubElement(attributes, 'xs:attribute', name=o_attr.name, type=type_name)
        else:
            logger.warn('unable to convert %s.%s : %s' % (o_obj.key_lett, o_attr.Name, s_dt.Name))
    return cls


def build_component(m, c_c):
    '''
    Build an xsd complex element out of a C_C, including its packaged S_DT and O_OBJ.
    '''
    component = ET.Element('xs:element', name=c_c.name)
    
    classes = ET.SubElement(component, 'xs:complexType')
    classes = ET.SubElement(classes, 'xs:sequence')
    
    scope_filter = lambda selected: is_contained_in(m, selected, c_c)
    
    for o_obj in m.select_many('O_OBJ', scope_filter):
        cls = build_class(m, o_obj)
        classes.append(cls)
    
    return component


def build_schema(m, c_c):
    '''
    Build an xsd schema from a bridgepoint component.
    '''
    schema = ET.Element('xs:schema')
    schema.set('xmlns:xs', 'http://www.w3.org/2001/XMLSchema')

    global_filter = lambda selected: is_global(m, selected)
    for s_dt in m.select_many('S_DT', global_filter):
        datatype = build_type(m, s_dt)
        if datatype is not None:
            schema.append(datatype)
    
    scope_filter = lambda selected: is_contained_in(m, selected, c_c)
    for s_dt in m.select_many('S_DT', scope_filter):
        datatype = build_type(m, s_dt)
        if datatype is not None:
            schema.append(datatype)
            
    component = build_component(m, c_c)
    schema.append(component)
    
    return schema


def prettify(xml_string):
    '''
    Indent an xml string with four spaces, and add an additional line break after each node.
    '''
    reparsed = xml.dom.minidom.parseString(xml_string)
    return reparsed.toprettyxml(indent="    ")


if __name__ == '__main__':
    
    parser = optparse.OptionParser(usage="%prog [OPTION]... {filename}", formatter=optparse.TitledHelpFormatter())
    parser.add_option("-c", "--component", dest="component", metavar="NAME", help="export xsd schema for the component named NAME", action="store", default=None)
    parser.add_option("-o", "--output", dest='output', metavar="PATH", action="store", help="save xsd schema to PATH", default=None)
    parser.add_option("-v", "--verbosity", dest='verbosity', action="count", help="increase debug logging level", default=1)
    
    (opts, args) = parser.parse_args()
    if len(args) == 0 or None in [opts.component, opts.output]:
        parser.print_help()
        sys.exit(1)
        
    levels = {
              0: logging.ERROR,
              1: logging.WARNING,
              2: logging.INFO,
              3: logging.DEBUG,
    }
    logging.basicConfig(level=levels.get(opts.verbosity, logging.DEBUG))
    
    loader = io.load.ModelLoader()
    loader.build_parser()
    loader.filename_input('%s/resources/ooaofooa_schema.sql' % base_dir)
    for filename in args:
        loader.filename_input(filename)
        
    m = loader.build_metamodel()
    
    c_c = m.select_any('C_C', lambda inst: inst.Name == opts.component)
    if c_c:
        schema = build_schema(m, c_c)
        with open(opts.output, 'w') as f:
            s = ET.tostring(schema, 'utf-8')
            s = prettify(s)
            f.write(s)
    else:
        logger.error('unable to find a component named %s' % opts.component)
        logger.info('available components to choose from are: %s' % ', '.join([c_c.Name for c_c in m.select_many('C_C')]))
            
        sys.exit(1)

