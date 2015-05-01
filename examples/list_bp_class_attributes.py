#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import sys
import xtuml

m = xtuml.load_metamodel(sys.argv[1:])

by_name = lambda inst: inst.Name
for o_obj in sorted(m.select_many('O_OBJ'), key=by_name):
    print(o_obj.Name)

    for o_attr in sorted(m.navigate_many(o_obj).O_ATTR[102](), key=by_name):
        s_dt = m.navigate_any(o_attr).S_DT[114]()
        print('   %s : %s' % (o_attr.Name, s_dt.Name))

