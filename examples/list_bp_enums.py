#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import sys

from xtuml import navigate_one as one
from bridgepoint import ooaofooa


if len(sys.argv) < 2:
    print('')
    print('  usage: %s <path to bridgepoint model folder>' % sys.argv[0])
    print('')
    sys.exit(1)

    
loader = ooaofooa.Loader()
loader.filename_input(sys.argv[1])
m = loader.build_metamodel()


get_name = lambda inst: one(inst).S_DT[17]().Name
for s_edt in sorted(m.select_many('S_EDT'), key=get_name):
    print(get_name(s_edt))

    is_first = lambda inst: not one(inst).S_ENUM[56, 'precedes']()
    s_enum = one(s_edt).S_ENUM[27](is_first)
    while s_enum:
        print('    %s' % s_enum.Name)
        s_enum = one(s_enum).S_ENUM[56, 'succeeds']()

