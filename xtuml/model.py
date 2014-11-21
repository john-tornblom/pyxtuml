# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import logging
import uuid
import copy

logger = logging.getLogger(__name__)
        

class NavChain(object):

    def __init__(self, metamodel, inst):
        self.metamodel = metamodel
        self.inst = inst

    def nav(self, kind, rel_id, phrase=None):
        inst = self.metamodel.navigate(self.inst, kind, rel_id)
        return NavChain(self.metamodel, inst)

    def __iter__(self):
        return self.inst.__iter__()
    
    def __call__(self):
        return self.inst
    
class AssociationEndPoint(object):
    
    def __init__(self, kind, cardinality, ids, phrase=None):
        self.cardinality = cardinality
        self.kind = kind
        self.phrase = phrase
        self.ids = ids
        

class SingleEndPoint(AssociationEndPoint):
    
    def __init__(self, kind, conditional=False, ids=[], phrase=None):
        if conditional: cardinality = '1C'
        else:           cardinality = '1'
        AssociationEndPoint.__init__(self, kind, cardinality, ids, phrase)


class ManyEndPoint(AssociationEndPoint):
    
    def __init__(self, kind, conditional=False, ids=[], phrase=None):
        if conditional: cardinality = 'MC'
        else:           cardinality = 'M'
        AssociationEndPoint.__init__(self, kind, cardinality, ids, phrase)
        


class MetaModel(object):

    def __init__(self):
        self.classes = dict()
        self.instances = dict()
        self.param_names = dict()
        self.param_types = dict()
        
    def define_class(self, kind, attributes):
        Cls = type(kind, (object,), dict(__r__=dict()))
        self.classes[kind] = Cls
        self.param_names[kind] = [name for name, _ in attributes]
        self.param_types[kind] = [ty for _, ty in attributes]
        
        return Cls

    def new(self, kind, *args, **kwargs):
        if kind not in self.classes.keys():
            logger.warning("Unknown class %s" % kind)
            return
        
        Cls = self.classes[kind]
        inst = Cls()
        inst.__r__ = copy.copy(Cls.__r__)
        
        # set all params with an initial default value
        def default_value(ty):
            if   ty == 'boolean'  : return False
            elif ty == 'integer'  : return 0
            elif ty == 'real'     : return 0.0
            elif ty == 'unique_id': return uuid.UUID(int=0)
            elif ty == 'string'   : return ''
            
            logger.error("Unknown data type '%s'" % ty)
        
        defaults = {key: default_value(ty) for key, ty in zip(self.param_names[kind], self.param_types[kind])}
        inst.__dict__.update(defaults)
        
        args = {key: value for key, value in zip(self.param_names[kind], args)}
        inst.__dict__.update(args)
        inst.__dict__.update(kwargs)
        
        if not self.instances.has_key(kind):
            self.instances[kind] = list()
            
        self.instances[kind].append(inst)
        
        return inst
        
    def empty(self, inst):
        if   inst is None: return True
        elif isinstance(inst, set): return len(inst) == 0
        return False
    
    def not_empty(self, inst):
        return not self.empty(inst)
    
    def cardinality(self, inst):
        if   inst is None: return 0
        elif isinstance(inst, set): return len(inst)
        else: return 1

    def _formalized_query(self, source, target):
        is_set = target.cardinality.startswith('M')
        
        def select_endpoint(inst, kwargs):
            keys = target.ids + kwargs.keys()
            values = [getattr(inst, name) for name in source.ids] + kwargs.values()
        
            if is_set: select = self.select_many
            else     : select = self.select_one
        
            kwargs = {key: value for key, value in zip(keys, values)}
            return select(target.kind, **kwargs)
        
        return lambda self, **kwargs: select_endpoint(self, kwargs)
    
    def define_relation(self, rel_id, end1, end2):
        Cls1 = self.classes[end1.kind]
        Cls2 = self.classes[end2.kind]
        
        Cls1.__r__['%s_%s' % (rel_id, end2.kind)] = self._formalized_query(end1, end2)
        Cls2.__r__['%s_%s' % (rel_id, end1.kind)] = self._formalized_query(end2, end1)
    
    def unrelate(self, inst1, inst2, rel_id, phrase=None, using=None):
        index1 = '%s_%s' % (rel_id, inst2.__class__.__name__)
        index2 = '%s_%s' % (rel_id, inst1.__class__.__name__)
        
        endpoint1 = inst1.__r__[index1]
        endpoint2 = inst2.__r__[index2]
        
        if isinstance(endpoint1, set):
            endpoint1 -= set([inst2])
        else:
            endpoint1 = None
            
        if isinstance(endpoint2, set):
            endpoint2 -= set([inst1])
        else:
            endpoint2 = None
        
        inst1.__r__[index1] = endpoint1
        inst2.__r__[index2] = endpoint2
        
    def relate(self, inst1, inst2, rel_id, phrase=None, using=None):
        index1 = '%s_%s' % (rel_id, inst2.__class__.__name__)
        index2 = '%s_%s' % (rel_id, inst1.__class__.__name__)
        
        endpoint1 = inst1.__r__[index1]
        endpoint2 = inst2.__r__[index2]
        
        if callable(endpoint1):
            endpoint1 = endpoint1(inst1)
        elif isinstance(endpoint1, set):
            endpoint1 |= set([inst2])
        else:
            endpoint1 = inst2
            
        if callable(endpoint2):
            endpoint2 = endpoint2(inst2)
        elif isinstance(endpoint2, set):
            endpoint2 |= set([inst1])
        else:
            endpoint2 = inst1
        
        inst1.__r__[index1] = endpoint1
        inst2.__r__[index2] = endpoint2
    
    def navigate(self, handle, kind, rel_id):
        if not isinstance(handle, set):
            handle = set([handle])

        index = '%s_%s' % (rel_id, kind)
        s = set()
        for inst in handle:
            r = inst.__r__[index]
            if callable(r):
                r = inst.__r__[index] = r(inst)
            
            if r is None:
                pass
            elif not isinstance(r, set):
                s |= set([r])
            else: 
                s |= r
            
        return s
        
    def chain(self, inst):
        return NavChain(self, inst)
    
    def select_one(self, kind, **kwargs):
        if not self.instances.has_key(kind): return
        
        Cls = self.classes[kind]
        for inst in self.instances[kind]:
            if not isinstance(inst, Cls): continue
            
            match = True
            for name, value in kwargs.items():
                if getattr(inst, name) != value:
                    match = False
                    break

            if match: return inst
    
    def select_any(self, kind, **kwargs):
        return self.select_one(kind, **kwargs)
    
    def select_many(self, kind, **kwargs):
        if not self.instances.has_key(kind): return set()
        
        Cls = self.classes[kind]
        lst = list()
        for inst in self.instances[kind]:
            if not isinstance(inst, Cls): continue
            
            match = True
            for name, value in kwargs.items():
                if getattr(inst, name) != value:
                    match = False
                    break

            if match: lst.append(inst)
            
        return set(lst)



