#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import sys
import os

base_dir = '%s/..' % os.path.dirname(__file__)
sys.path.append(base_dir)

from xtuml import io

loader = io.load.ModelLoader()
loader.build_parser()
loader.filename_input('%s/resources/ooaofooa_schema.sql' % base_dir)
loader.filename_input(sys.argv[1])


m = loader.build_metamodel()
for o_obj in m.select_many('O_OBJ'):
    print (o_obj.Name)

    for o_attr in m.navigate_many(o_obj).O_ATTR[102]():
        s_dt = m.navigate_any(o_attr).S_DT[114]()
        print ('   %s : %s' % (o_attr.Name, s_dt.Name))

