# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from itertools import chain

import logging
import uuid
import collections

try:
    from future_builtins import filter, zip
except ImportError:
    pass


logger = logging.getLogger(__name__)


class ModelException(Exception):
    pass


class NavChain(object):
    
    def __init__(self, handle, is_many=True):
        if handle is None:
            self.handle = QuerySet()
        
        elif isinstance(handle, BaseObject):
            self.handle = QuerySet([handle])
        
        elif isinstance(handle, QuerySet):
            self.handle = handle
        
        else:
            raise ModelException("Unable to navigate instances of '%s'" % type(handle))
            
        self.is_many = is_many
        self._kind = None
    
    def nav(self, kind, relid, phrase=''):
        if isinstance(relid, int):
            relid = 'R%d' % relid
        
        result = QuerySet()
        for child in iter(self.handle):
            result |= child.__q__[kind][relid][phrase](child)

        self.handle = result
        
        return self
    
    def __getattr__(self, name):
        self._kind = name
        return self
    
    def __getitem__(self, args):
        if not isinstance(args, tuple):
            args = (args, '')
        
        relid, phrase = args
        
        return self.nav(self._kind, relid, phrase)

    def __call__(self, where_clause=None):
        s = filter(where_clause, self.handle)
        if self.is_many:
            return QuerySet(s)
        else:
            return next(s, None)


def navigate_one(inst):
    return navigate_any(inst)


def navigate_any(inst):
    return NavChain(inst, is_many=False)


def navigate_many(inst):
    return NavChain(inst, is_many=True)


class Association(object):
    
    def __init__(self, relid, source, target):
        self.id = relid
        self.source = source
        self.target = target    


class AssociationLink(object):
    
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


class SingleAssociationLink(AssociationLink):
    
    def __init__(self, kind, conditional=False, ids=[], phrase=''):
        if conditional: cardinality = '1C'
        else:           cardinality = '1'
        AssociationLink.__init__(self, kind, cardinality, ids, phrase)


class ManyAssociationLink(AssociationLink):
    
    def __init__(self, kind, conditional=False, ids=[], phrase=''):
        if conditional: cardinality = 'MC'
        else:           cardinality = 'M'
        AssociationLink.__init__(self, kind, cardinality, ids, phrase)
        

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
    __r__ = None  # store relations
    __q__ = None  # store predefined queries
    __c__ = None  # store a cached results from queries
    __a__ = None  # store a list of attributes (name, type)
    __m__ = None  # store a handle to the metamodel which created the instance
    
    def __init__(self):
        self.__c__.clear()
        
    def __add__(self, other):
        assert isinstance(other, BaseObject)
        return QuerySet([self, other])

    def __sub__(self, other):
        assert isinstance(other, BaseObject)
        if self == other: return QuerySet()
        else: return QuerySet([self])

    def __getattr__(self, name):
        lname = name.lower()
        for attr in self.__dict__.keys():
            if attr.lower() == lname:
                return self.__dict__[attr]

        object.__getattribute__(self, name)
    
    def __setattr__(self, name, value):
        name = name.lower()
        for attr in self.__dict__.keys():
            if attr.lower() == name:
                self.__dict__[attr] = value
                self.__c__.clear()
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
    id_generator = None
    ignore_undefined_classes = False
    
    def __init__(self, id_generator=IdGenerator()):
        self.classes = dict()
        self.instances = dict()
        self.id_generator = id_generator
        
    def define_class(self, kind, attributes):
        '''
        Define a new class in the meta model.
        '''
        Cls = type(kind, (BaseObject,), dict(__r__=dict(), __q__=dict(),
                                             __c__=dict(), __m__=self,
                                             __a__=attributes))
        self.classes[kind] = Cls
        
        return Cls
    
    def default_value(self, ty_name):
        '''
        Obtain the default value for a named meta model type.
        '''
        if   ty_name == 'boolean': return False
        elif ty_name == 'integer': return 0
        elif ty_name == 'integer': return 0
        elif ty_name == 'real': return 0.0
        elif ty_name == 'string': return ''
        elif ty_name == 'unique_id': return next(self.id_generator)
        else: raise ModelException("Unknown type named '%s'" % ty_name)
    
    def type_name(self, ty):
        '''
        Determine the named meta model type of a python type, 
            e.g. bool --> boolean.
        '''
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
        '''
        Determine the python-type of a named meta model type, 
            e.g. boolean --> bool.
        '''
        lookup_table = {
          'boolean'     : bool,
          'integer'     : int,
          'real'        : float,
          'string'      : str,
          'inst_ref'    : BaseObject,
          'inst_ref_set': QuerySet,
          'unique_id'   : type(self.id_generator.peek())
        }
        
        if name in lookup_table:
            return lookup_table[name]
        else:
            raise ModelException("Unknown type named '%s'" % name)
        
    def new(self, kind, *args, **kwargs):
        '''
        Create a new meta model instance of some kind.
        '''
        if kind not in self.classes:
            if not self.ignore_undefined_classes:
                raise ModelException("Unknown class %s" % kind)
            else:
                return
            
        Cls = self.classes[kind]
        inst = Cls()
        
        # set all parameters with an initial default value
        for name, ty in inst.__a__:
            inst.__dict__[name] = self.default_value(ty)

        # set all positional arguments
        for attr, value in zip(inst.__a__, args):
            name, ty = attr
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
    def empty(arg):
        '''
        Determine if arg is empty
        '''
        if   arg is None: return True
        elif isinstance(arg, QuerySet): return len(arg) == 0
        return False
    
    @staticmethod
    def not_empty(arg):
        '''
        Determine if arg is not empty
        '''
        return not MetaModel.empty(arg)
    
    @staticmethod
    def cardinality(arg):
        '''
        Determine the cardinality of arg.
        '''
        if   arg is None: return 0
        elif isinstance(arg, QuerySet): return len(arg)
        else: return 1

    @staticmethod
    def is_set(arg):
        '''
        Determine if arg is a set of meta model instances.
        '''
        return isinstance(arg, QuerySet)
    
    @staticmethod
    def is_instance(arg):
        '''
        Determine if arg is a meta model instance.
        '''
        return isinstance(arg, BaseObject)
    
    @staticmethod
    def first(inst, query_set):
        '''
        Determine if an instance is the first item in a query set.
        '''
        assert isinstance(query_set, QuerySet)
        return inst == query_set.first
    
    @staticmethod
    def not_first(inst, query_set):
        '''
        Determine if an instance is not the first item in a query set.
        '''
        assert isinstance(query_set, QuerySet)
        return inst != query_set.first
    
    @staticmethod
    def last(inst, query_set):
        '''
        Determine if an instance is the last item in a query set.
        '''
        assert isinstance(query_set, QuerySet)
        return inst == query_set.last

    @staticmethod
    def not_last(inst, query_set):
        '''
        Determine if an instance is not the last item in a query set.
        '''
        assert isinstance(query_set, QuerySet)
        return inst != query_set.last
    
    def _query(self, kind, many, **kwargs):
        for inst in iter(self.instances[kind]):
            for name, value in kwargs.items():
                if getattr(inst, name) != value:
                    break
            else:
                yield inst
                if not many:
                    return
                    
    def _select_endpoint(self, inst, source, target, kwargs):
        if not target.kind in self.instances:
            return QuerySet()
        
        keys = chain(target.ids, kwargs.keys())
        values = chain([getattr(inst, name) for name in source.ids], kwargs.values())
        kwargs = dict(zip(keys, values))
                            
        cache_key = frozenset(list(kwargs.items()))
        cache = self.classes[target.kind].__c__
        
        if cache_key not in cache:
            cache[cache_key] = QuerySet(self._query(target.kind, target.is_many, **kwargs))
            
        return cache[cache_key]
    
    def _formalized_query(self, source, target):
        return lambda inst, **kwargs: self._select_endpoint(inst, source, target, kwargs)
    
    def define_relation(self, rel_id, source, target):
        '''
        Define a directed association from source to target.
        '''
        return self.define_association(rel_id, source, target)
    
    def define_association(self, rel_id, source, target):
        '''
        Define a directed association from source to target.
        '''
        ass = Association(rel_id, source, target)
        
        Source = self.classes[source.kind]
        Target = self.classes[target.kind]

        if rel_id not in Source.__r__:
            Source.__r__[rel_id] = set()
            
        if rel_id not in Target.__r__:
            Target.__r__[rel_id] = set()
            
        Source.__r__[rel_id].add(ass)
        Target.__r__[rel_id].add(ass)
        
        if target.kind not in Source.__q__:
            Source.__q__[target.kind] = dict()
            
        if source.kind not in Target.__q__:
            Target.__q__[source.kind] = dict()
        
        if rel_id not in Source.__q__[target.kind]:
            Source.__q__[target.kind][rel_id] = dict()
            
        if rel_id not in Target.__q__[source.kind]:
            Target.__q__[source.kind][rel_id] = dict()
        
        Source.__q__[target.kind][rel_id][target.phrase] = self._formalized_query(source, target)
        Target.__q__[source.kind][rel_id][source.phrase] = self._formalized_query(target, source)
    
    def select_one(self, kind, where_cond=None):
        '''
        Query the model for an instance.
        '''
        return self.select_any(kind, where_cond)
    
    def select_any(self, kind, where_cond=None):
        '''
        Query the model for an instance.
        '''
        if kind in self.instances:
            s = filter(where_cond, self.instances[kind])
            return next(s, None)
        
    def select_many(self, kind, where_cond=None):
        '''
        Query the model for a set of instances.
        '''
        if kind in self.instances:
            return QuerySet(filter(where_cond, self.instances[kind]))
        else:
            return QuerySet()


def _find_association_links(inst1, inst2, rel_id, phrase):
    '''
    Find association links which correspond to the given arguments.
    '''
    if isinstance(rel_id, int):
        rel_id = 'R%d' % rel_id
    
    kind1 = inst1.__class__.__name__
    kind2 = inst2.__class__.__name__
    
    if (rel_id not in inst1.__r__ or
        rel_id not in inst2.__r__):
        raise ModelException('Unknown association %s---(%s)---%s' % (kind1,
                                                                     rel_id,
                                                                     kind2))
    for ass in chain(inst1.__r__[rel_id], inst2.__r__[rel_id]):
        if  (kind1 == ass.source.kind and 
             kind2 == ass.target.kind and 
             ass.source.phrase == phrase):
            return ass.source, ass.target
        
        elif (kind1 == ass.target.kind and 
              kind2 == ass.source.kind and 
              ass.target.phrase == phrase):
            return ass.target, ass.source

    raise ModelException("Unknown association %s---(%s.'%s')---%s" % (kind1,
                                                                      rel_id,
                                                                      phrase,
                                                                      kind2))


def _defered_relate(from_inst, to_inst, rel_id, phrase):
    return lambda: relate(from_inst, to_inst, rel_id, phrase)


def _defered_batch_relate(inst, end):
    '''
    Generate list of deferred relates which needs to be invoked after an 
    update to identifying attributes on the association end point is made.
    '''
    kind = inst.__class__.__name__
    l = list()
    for ass in chain(*inst.__r__.values()):
        if end in [ass.target, ass.source]:
            continue
        if kind != ass.target.kind:
            continue
        elif len(set(end.ids) & set(ass.source.ids)) == 0:
            continue
        
        nav = navigate_many(inst).nav(ass.source.kind, ass.id, ass.source.phrase)
        for from_inst in nav():
            fn = _defered_relate(from_inst, inst, ass.id, ass.source.phrase)
            l.append(fn)

    return l


def relate(from_inst, to_inst, rel_id, phrase=''):
    '''
    Relate two instances to each other by copying the identifying attributes
    from the instance on the TO side of a association to the instance on the
    FROM side. Updated values which affect existing associations are propagated.
    
    NOTE: Reflexive associations require a phrase, and that the order amongst
    the instances is as intended.
    '''
    from_end, to_end = _find_association_links(from_inst, to_inst, rel_id, phrase)
    post_process = _defered_batch_relate(from_inst, from_end)
        
    for from_attr, to_attr in zip(from_end.ids, to_end.ids):
        value = getattr(to_inst, to_attr)
        setattr(from_inst, from_attr, value)
    
    for defered_relate in post_process:
        defered_relate()

    
def unrelate(from_inst, to_inst, rel_id, phrase=''):
    '''
    Unrelate two instances from each other by reseting the identifying
    attributes on the FROM side of the association.
    
    NOTE: Reflexive associations require a phrase, and that the order amongst
    the instances is as intended.
    '''
    from_end, _ = _find_association_links(from_inst, to_inst, rel_id, phrase)
    for name, ty in from_inst.__a__:
        if name in from_end.ids:
            value = from_inst.__m__.default_value(ty)
            setattr(from_inst, name, value)


