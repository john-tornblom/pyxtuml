#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2016 John Törnblom

import sys
import logging
import re
import xtuml

from xtuml import navigate_one as one
from xtuml import navigate_many as many
from bridgepoint import ooaofooa


logger = logging.getLogger('schema_gen')


def parse_keyword(expr, keyword):
    regexp = re.compile(keyword + ":([^\n]*)")
    result = regexp.search(expr)
        
    if result:
        return result.groups()[0].strip().lower()
    else:
        return ''

    
def o_attr_filter(o_attr):
    description = o_attr.Descrip.lower()
    keymap = dict(persistent='false',
                  translate_for_external_use='false')
                  
    for key, value in keymap.items():
        if parse_keyword(description, key) == value:
            return True
    

def main():
    if len(sys.argv) < 2:
        logger.info('usage: %s <path to ooaofooa model folder>' % sys.argv[0])
        sys.exit(1)
        
    loader = ooaofooa.Loader()
    for filename in sys.argv[1:]:
        loader.filename_input(filename)
    
    m = loader.build_metamodel()
    c = loader.build_component()
    
    for o_obj in m.select_many('O_OBJ'):
        for o_attr in many(o_obj).O_ATTR[102](o_attr_filter):
            logger.info('Filtering %s.%s' % (o_obj.Key_Lett, o_attr.Name))
            metaclass = c.find_metaclass(o_obj.Key_Lett)
            metaclass.delete_attribute(o_attr.Name)
            
    xtuml.persist_schema(c, '/dev/stdout')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
    




