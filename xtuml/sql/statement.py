# encoding: utf-8
# Copyright (C) 2014 John Törnblom

class InsertStmt(object):
    def __init__(self, kind):
        self.kind = kind
        self.values = list()
        
class CreateStmt(object):
    def __init__(self, kind):
        self.kind = kind
        self.attributes = list()

class RelateStmt(object):
    def __init__(self, rel_id):
        self.id = rel_id
        self.end_points = list()
