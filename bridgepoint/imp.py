# encoding: utf-8
# Copyright (C) 2015-2016 John Törnblom

import sys
import os.path

from bridgepoint import ooaofooa


def _get_version(filename):
    with open(filename, 'r') as f:
        line = f.readline()
        _, value = line.split("persistence-version: ", 1)
        return  value.strip()


def _check_magic(filename):
    if not os.path.exists(filename):
        return False
    
    with open(filename, 'r') as f:
        line = f.readline()
        return 'content: SystemModel' in line


class ModelImporter(object):
    
    def __init__(self, path):
        self.path = path
        
    @classmethod
    def find_module(cls, fullname, paths=None):
        if paths is None:
            paths = sys.path
                        
        names = fullname.split('.')
        model_name = names[-1]
        
        for f in paths:
            path = os.path.join(os.path.realpath(f), 'models')
            path = os.path.join(path, model_name)
            source = os.path.join(path, model_name + '.xtuml')
            if _check_magic(source):
                return cls(path)
    
    def get_code(self, module):
        pass

    def get_data(self, module):
        pass

    def get_filename(self, name):
        pass

    def get_source(self, name):
        pass

    def is_package(self, *args, **kwargs):
        return False

    def load_module(self, fullname):
        l = ooaofooa.Loader()
        l.filename_input(self.path)
        return l


def install():
    if ModelImporter not in sys.meta_path:
        sys.meta_path.append(ModelImporter)


def remove():
    sys.meta_path.remove(ModelImporter)

