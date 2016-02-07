#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import sys

from xtuml import navigate_one as one
from xtuml import navigate_many as many
from bridgepoint import ooaofooa


if len(sys.argv) < 2:
    print('')
    print('  usage: %s <path to bridgepoint model folder>' % sys.argv[0])
    print('')
    sys.exit(1)

    
m = ooaofooa.load_metamodel(sys.argv[1])


by_name = lambda inst: inst.Name
for o_obj in sorted(m.select_many('O_OBJ'), key=by_name):
    print(o_obj.Name)

    for o_attr in sorted(many(o_obj).O_ATTR[102](), key=by_name):
        s_dt = one(o_attr).S_DT[114]()
        print('   %s : %s' % (o_attr.Name, s_dt.Name))

