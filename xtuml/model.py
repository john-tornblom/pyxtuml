# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import logging
import uuid
import collections


logger = logging.getLogger(__name__)


class ModelException(Exception):
    pass


class NavChain(object):

    def __init__(self, metamodel, inst):
        self.metamodel = metamodel
        self.inst = inst

    def nav(self, kind, rel_id, phrase=''):
        inst = self.metamodel.navigate(self.inst, kind, rel_id, phrase)
        return NavChain(self.metamodel, inst)

    def __iter__(self):
        return self.inst.__iter__()
    
    def __call__(self):
        return self.inst


class AssociationEndPoint(object):
    
    def __init__(self, kind, cardinality, ids, phrase=''):
        self.cardinality = cardinality
        self.kind = kind
        self.phrase = phrase
        self.ids = ids

    @property
    def is_many(self):
        return self.cardinality.upper() in ['M', 'MC']

    @property
    def is_conditional(self):
        return 'C' in self.cardinality.upper()


class SingleEndPoint(AssociationEndPoint):
    
    def __init__(self, kind, conditional=False, ids=[], phrase=''):
        if conditional: cardinality = '1C'
        else:           cardinality = '1'
        AssociationEndPoint.__init__(self, kind, cardinality, ids, phrase)


class ManyEndPoint(AssociationEndPoint):
    
    def __init__(self, kind, conditional=False, ids=[], phrase=''):
        if conditional: cardinality = 'MC'
        else:           cardinality = 'M'
        AssociationEndPoint.__init__(self, kind, cardinality, ids, phrase)
        

class OrderedSet(collections.MutableSet):
    # Originally posted on http://code.activestate.com/recipes/576694
    # by Raymond Hettinger.
    
    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next_ = self.map.pop(key)
            prev[2] = next_
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        
        if last:
            key = self.end[1][0]
        else:
            key = self.end[2][0]
            
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


class QuerySet(OrderedSet):
    
    @property
    def first(self):
        if len(self):
            return next(iter(self))
    
    @property
    def last(self):
        if len(self):
            return next(reversed(self))


class BaseObject(object):
    __r__ = None
    __q__ = None
    
    def __add__(self, other):
        assert isinstance(other, BaseObject)
        return QuerySet([self, other])

    def __sub__(self, other):
        assert isinstance(other, BaseObject)
        if self == other: return QuerySet()
        else: return QuerySet([self])

    def __getattr__(self, name):
        name = name.lower()
        for attr in self.__dict__.keys():
            if attr.lower() == name:
                return self.__dict__[attr]

    def __setattr__(self, name, value):
        name = name.lower()
        for attr in self.__dict__.keys():
            if attr.lower() == name:
                self.__dict__[attr] = value
                return

    def __str__(self):
        return str(self.__dict__)
    
    
class IdGenerator(object):
    
    def __init__(self, readfunc=uuid.uuid4):
        self.readfunc = readfunc
        self._current = readfunc()
    
    def peek(self):
        return self._current
    
    def next(self):
        val = self._current
        self._current = self.readfunc()
        return val
    
    def __iter__(self):
        return self

    def __next__(self):
        return self.next()


class MetaModel(object):
    
    classes = None
    instances = None
    param_names = None
    param_types = None
    id_generator = None
    
    def __init__(self, id_generator=IdGenerator()):
        self.classes = dict()
        self.instances = dict()
        self.param_names = dict()
        self.param_types = dict()
        self.id_generator = id_generator
        
    def define_class(self, kind, attributes):
        Cls = type(kind, (BaseObject,), dict(__q__=dict(), __r__=dict()))
        self.classes[kind] = Cls
        self.param_names[kind] = [name for name, _ in attributes]
        self.param_types[kind] = [ty for _, ty in attributes]
        
        return Cls
    
    def default_value(self, ty_name):
        if   ty_name == 'boolean': return False
        elif ty_name == 'integer': return 0
        elif ty_name == 'integer': return 0
        elif ty_name == 'real': return 0.0
        elif ty_name == 'string': return ''
        elif ty_name == 'unique_id': return next(self.id_generator)
        else: raise ModelException("Unknown type named '%s'" % ty_name)
    
    def type_name(self, ty):
        if   issubclass(ty, bool): return 'boolean'
        elif issubclass(ty, int): return 'integer'
        elif issubclass(ty, float): return 'real'
        elif issubclass(ty, str): return 'string'
        elif issubclass(ty, BaseObject): return 'inst_ref'
        elif issubclass(ty, type(None)): return 'inst_ref'
        elif issubclass(ty, QuerySet): return 'inst_ref_set'
        elif issubclass(ty, type(self.id_generator.peek())): return 'unique_id'
        else: raise ModelException("Unknown type '%s'" % ty.__name__)
        
    def named_type(self, name):
        lookup_table = {
          'boolean'     : bool,
          'integer'     : int,
          'real'        : float,
          'string'      : str,
          'inst_ref'    : BaseObject,
          'inst_ref_set': QuerySet,
          'unique_id'   : type(self.id_generator.peek())
        }
        
        if name in  lookup_table:
            return lookup_table[name]
        else:
            raise ModelException("Unknown type named '%s'" % name)
        
    def new(self, kind, *args, **kwargs):
        if kind not in self.classes:
            raise ModelException("Unknown class %s" % kind)
        
        Cls = self.classes[kind]
        inst = Cls()

        # set all parameters with an initial default value
        for key, ty in zip(self.param_names[kind], self.param_types[kind]):
            inst.__dict__[key] = self.default_value(ty)

        # set all positional arguments
        for name, ty, value in zip(self.param_names[kind], self.param_types[kind], args):
            Type = self.named_type(ty)
            if not isinstance(value, Type):
                value = Type(value)
                
            inst.__dict__[name] = value

        # set all named arguments
        inst.__dict__.update(kwargs)

        if not kind in self.instances:
            self.instances[kind] = list()
            
        self.instances[kind].append(inst)
        
        return inst
        
    @staticmethod
    def empty(inst):
        if   inst is None: return True
        elif isinstance(inst, QuerySet): return len(inst) == 0
        return False
    
    @staticmethod
    def not_empty(inst):
        return not MetaModel.empty(inst)
    
    @staticmethod
    def cardinality(inst):
        if   inst is None: return 0
        elif isinstance(inst, QuerySet): return len(inst)
        else: return 1

    @staticmethod
    def is_set(inst):
        return isinstance(inst, QuerySet)
    
    @staticmethod
    def is_instance(inst):
        return isinstance(inst, BaseObject)
    
    @staticmethod
    def first(inst, query_set):
        assert isinstance(query_set, QuerySet)
        return inst == query_set.first
    
    @staticmethod
    def not_first(inst, query_set):
        assert isinstance(query_set, QuerySet)
        return inst != query_set.first
    
    @staticmethod
    def last(inst, query_set):
        assert isinstance(query_set, QuerySet)
        return inst == query_set.last

    @staticmethod
    def not_last(inst, query_set):
        assert isinstance(query_set, QuerySet)
        return inst != query_set.last
    
    def _formalized_query(self, source, target):
        is_set = target.cardinality.startswith('M')
        
        def select_endpoint(inst, kwargs):
            keys = target.ids + list(kwargs.keys())
            values = [getattr(inst, name) for name in source.ids] + list(kwargs.values())

            if is_set: select = self.select_many
            else     : select = self.select_one
        
            kwargs = dict()
            for key, value in zip(keys, values):
                kwargs[key] = value
    
            return select(target.kind, **kwargs)
            
        return lambda self, **kwargs: select_endpoint(self, kwargs)
    
    def define_relation(self, rel_id, end1, end2):
        Cls1 = self.classes[end1.kind]
        Cls2 = self.classes[end2.kind]

        Cls1.__r__['%s_%s_%s' % (rel_id, end2.kind, end2.phrase)] = end2
        Cls2.__r__['%s_%s_%s' % (rel_id, end1.kind, end1.phrase)] = end1
        
        Cls1.__q__['%s_%s_%s' % (rel_id, end2.kind, end2.phrase)] = self._formalized_query(end1, end2)
        Cls2.__q__['%s_%s_%s' % (rel_id, end1.kind, end1.phrase)] = self._formalized_query(end2, end1)

    def navigate(self, handle, kind, rel_id, phrase=''):
        index = '%s_%s_%s' % (rel_id, kind, phrase)

        if handle is None:
            handle = QuerySet()
        
        elif isinstance(handle, BaseObject):
            handle = QuerySet([handle])
            
        elif not isinstance(handle, QuerySet):
            raise ModelException("Unable to navigate instances of '%s'" % type(handle))

        s = QuerySet()
        for inst in handle:
            query = inst.__q__[index]
            result = query(inst)
            
            if result is None:
                pass
            
            elif not isinstance(result, QuerySet):
                s |= QuerySet([result])
                
            else: 
                s |= result

        return s
        
    def chain(self, inst):
        return NavChain(self, inst)
    
    def select_one(self, kind, **kwargs):
        if not kind in self.classes:
            raise ModelException("The kind '%s' is undefined" % kind)
        
        if not kind in self.instances:
            return QuerySet()
        
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
        if not kind in self.classes:
            raise ModelException("The kind '%s' is undefined" % kind)
        
        if not kind in self.instances:
            return QuerySet()
        
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
            
        return QuerySet(lst)


