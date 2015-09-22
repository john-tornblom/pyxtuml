# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from itertools import chain
from functools import partial

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
    '''
    A navigation chain initializes a query from one or more instances.
    Queries may be syntactically cascaded in several ways:
    
       res = NavChain(inst).nav('X', 'R100', 'phrase').nav('Y', 101)

    or using an OAL/RSL inspired syntax:
    
       res = NavChain(inst).X[100, 'phrase'].Y[101](lamda x: <filter expression>)
    '''
    
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
        kind = kind.upper()
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


class Association(object):
    '''
    An association connects two classes to each other via two association links.
    '''
    
    def __init__(self, relid, source, target):
        if isinstance(relid, int):
            relid = 'R%d' % relid
        self.id = relid
        self.source = source
        self.target = target    

    @property
    def is_reflexive(self):
        return self.source.kind == self.target.kind

    
class AssociationLink(object):
    '''
    An association link represent an end point in an association.
    '''
    
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
    '''
    An association link that identifies an end point with cardinality 0..1 or 1.
    '''
    
    def __init__(self, kind, conditional=False, ids=[], phrase=''):
        if conditional: cardinality = '1C'
        else:           cardinality = '1'
        AssociationLink.__init__(self, kind, cardinality, ids, phrase)


class ManyAssociationLink(AssociationLink):
    '''
    An association link that identifies an end point with cardinality * or 1..*.
    '''
    
    def __init__(self, kind, conditional=False, ids=[], phrase=''):
        if conditional: cardinality = 'MC'
        else:           cardinality = 'M'
        AssociationLink.__init__(self, kind, cardinality, ids, phrase)
        

class OrderedSet(collections.MutableSet):
    '''
    Set that remembers original insertion order.
    '''
    # Originally posted on http://code.activestate.com/recipes/576694
    # by Raymond Hettinger.
    
    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next_ = self.map.pop(key)
            prev[2] = next_
            next_[1] = prev

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        
        if last:
            key = self.end[1][0]
        else:
            key = self.end[2][0]
            
        self.discard(key)
        return key
    
    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

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

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if not isinstance(other, OrderedSet):
            return self == OrderedSet(iter(other))
        
        if not len(self) == len(other):
            return False
        
        return list(self) == list(other)


class QuerySet(OrderedSet):
    '''
    An ordered set which holds instances that match queries from a meta model.
    '''
    
    @property
    def first(self):
        if len(self):
            return next(iter(self))
    
    @property
    def last(self):
        if len(self):
            return next(reversed(self))


class BaseObject(object):
    '''
    A common base object for all instances created in a meta model. Accesses 
    to attributes, e.g. getattr/setattr, on these objects are case insensitive.
    '''
    __r__ = None  # store relations
    __q__ = None  # store predefined queries
    __m__ = None  # store a handle to the meta model which created the instance
    __c__ = dict()  # store a cached results from queries
    __a__ = list()  # store a list of attributes (name, type)
    __i__ = set() # set of identifying attributes
    __d__ = set() # set of derived attributes
    
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
        uname = name.upper()
        for attr, _ in self.__a__:
            if attr.upper() == uname:
                return self.__dict__[attr]

        return object.__getattribute__(self, name)
    
    def __setattr__(self, name, value):
        uname = name.upper()
        for attr, _ in self.__a__:
            if attr.upper() == uname:
                self.__dict__[attr] = value
                self.__c__.clear()
                return

        self.__dict__[name] = value
        
    def __str__(self):
        return str(self.__dict__)
    
    
class IdGenerator(object):
    '''
    Base class for generating unique identifiers in a meta model.
    '''
    
    readfunc = None

    def __init__(self):
        '''
        Initialize an id generator with a start value.
        '''
        self._current = self.readfunc()
    
    def peek(self):
        '''
        Peek at the current value without progressing to the next one.
        '''
        return self._current
    
    def next(self):
        '''
        Progress to the next identifier, and return the current one.
        '''
        val = self._current
        self._current = self.readfunc()
        return val
    
    def __iter__(self):
        return self

    def __next__(self):
        return self.next()


class UUIDGenerator(IdGenerator):
    '''
    A uuid-based unique id generator for meta models.
    '''
    def readfunc(self):
        return uuid.uuid4().int


class IntegerGenerator(IdGenerator):
    '''
    An integer-based unique id generator for meta models.
    '''
    
    _current = 0
    def readfunc(self):
        return self._current + 1


def _is_null(inst, name):
    value = getattr(inst, name)
    if value:
        return False
    
    elif value is None:
        return True

    name = name.upper()
    for attr_name, attr_ty in inst.__a__:
        attr_name.upper()
        if attr_name != name:
            continue

        attr_ty = attr_ty.upper()
        if attr_ty == 'UNIQUE_ID':
            # UUID(int=0) is reserved for null
            return value == 0

        elif attr_ty == 'STRING':
            # empty string is reserved for null
            return len(value) == 0

        else:
            #null-values for integer, boolean and real are not supported
            return False

        
class MetaModel(object):
    '''
    A meta model contains class definitions with associations between them,
    and instances of different class definitions.
    '''
    
    classes = None
    instances = None
    associations = None
    id_generator = None
    ignore_undefined_classes = False
    
    def __init__(self, id_generator=None):
        '''
        Create a new, empty meta model. 
        Optionally, specify an id generator used to obtain unique identifiers.
        '''
        if id_generator is None:
            id_generator = UUIDGenerator()
            
        self.classes = dict()
        self.instances = dict()
        self.associations = list()
        self.id_generator = id_generator
        
    def define_class(self, kind, attributes, doc=''):
        '''
        Define and return a new class in the meta model.
        '''
        ukind = kind.upper()
        if ukind in self.classes.keys() or ukind in self.instances.keys():
            raise ModelException('A class with the name %s is already defined' % kind)
    
        Cls = type(kind, (BaseObject,), dict(__r__=dict(), __q__=dict(),
                                             __c__=dict(), __m__=self,
                                             __i__=set(), __d__=set(),
                                             __a__=attributes, __doc__=doc))
        self.classes[ukind] = Cls
        self.instances[ukind] = list()
        
        return Cls

    def new(self, kind, *args, **kwargs):
        '''
        Create and return a new meta model instance of some kind.
        '''
        ukind = kind.upper()
        if ukind not in self.classes:
            if not self.ignore_undefined_classes:
                raise ModelException("Unknown class %s" % kind)
            else:
                return
            
        Cls = self.classes[ukind]
        inst = Cls()
        
        # set all attributes with an initial default value
        for name, ty in inst.__a__:
            if name in inst.__d__:
                value = None
            else:
                value = self._default_value(ty)
            setattr(inst, name, value)
            
        # set all positional arguments
        for attr, value in zip(inst.__a__, args):
            name, ty = attr
            setattr(inst, name, value)
            
        # set all named arguments
        for name, value in kwargs.items():
            setattr(inst, name, value)
            
        self.instances[ukind].append(inst)
        
        return inst

    def define_relation(self, rel_id, source, target):
        '''
        Define and return an association between source to target.
        '''
        return self.define_association(rel_id, source, target)
    
    def define_association(self, rel_id, source, target):
        '''
        Define and return an association between source to target.
        '''
        ass = Association(rel_id, source, target)
        self.associations.append(ass)
        
        source_kind = source.kind.upper()
        target_kind = target.kind.upper()
        
        Source = self.classes[source_kind]
        Target = self.classes[target_kind]

        Source.__d__ |= set(ass.source.ids)
        Target.__i__ |= set(ass.target.ids)
        
        if ass.id not in Source.__r__:
            Source.__r__[ass.id] = set()
            
        if ass.id not in Target.__r__:
            Target.__r__[ass.id] = set()
            
        Source.__r__[ass.id].add(ass)
        Target.__r__[ass.id].add(ass)
        
        if target_kind not in Source.__q__:
            Source.__q__[target_kind] = dict()
            
        if source_kind not in Target.__q__:
            Target.__q__[source_kind] = dict()
        
        if ass.id not in Source.__q__[target_kind]:
            Source.__q__[target_kind][ass.id] = dict()
            
        if ass.id not in Target.__q__[source_kind]:
            Target.__q__[source_kind][ass.id] = dict()
        
        Source.__q__[target_kind][ass.id][target.phrase] = self._formalized_query(source, target)
        Target.__q__[source_kind][ass.id][source.phrase] = self._formalized_query(target, source)
    
        return ass
    
    def select_one(self, kind, where_cond=None):
        '''
        Query the model for an instance.
        '''
        return self.select_any(kind, where_cond)
    
    def select_any(self, kind, where_cond=None):
        '''
        Query the model for an instance.
        '''
        ukind = kind.upper()
        if ukind not in self.instances:
            if not self.ignore_undefined_classes:
                raise ModelException("Unknown class %s" % kind)
            return None

        s = filter(where_cond, self.instances[ukind])
        return next(s, None)
        
    def select_many(self, kind, where_cond=None):
        '''
        Query the model for a set of instances.
        '''
        ukind = kind.upper()
        if ukind not in self.instances:
            if not self.ignore_undefined_classes:
                raise ModelException("Unknown class %s" % kind)
            return QuerySet()

        return QuerySet(filter(where_cond, self.instances[ukind]))

    def _default_value(self, ty_name):
        '''
        Obtain the default value for a named meta model type.
        '''
        uname = ty_name.upper()
        if   uname == 'BOOLEAN': return False
        elif uname == 'INTEGER': return 0
        elif uname == 'REAL': return 0.0
        elif uname == 'STRING': return ''
        elif uname == 'UNIQUE_ID': return next(self.id_generator)
        else: raise ModelException("Unknown type named '%s'" % ty_name)
        
    def _query(self, kind, many, **kwargs):
        for inst in iter(self.instances[kind]):
            for name, value in kwargs.items():
                if _is_null(inst, name) or getattr(inst, name) != value:
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
    

def _find_association_links(inst1, inst2, rel_id, phrase):
    '''
    Find association links which correspond to the given arguments.
    '''
    if isinstance(rel_id, int):
        rel_id = 'R%d' % rel_id
    
    kind1 = inst1.__class__.__name__.upper()
    kind2 = inst2.__class__.__name__.upper()
    
    if (rel_id not in inst1.__r__ or
        rel_id not in inst2.__r__):
        raise ModelException('Unknown association %s---(%s)---%s' % (kind1,
                                                                     rel_id,
                                                                     kind2))
    for ass in chain(inst1.__r__[rel_id], inst2.__r__[rel_id]):
        if  (kind1 == ass.source.kind and 
             kind2 == ass.target.kind and 
             ass.source.phrase == phrase):
            return inst1, inst2, ass
        
        elif (kind1 == ass.target.kind and 
              kind2 == ass.source.kind and 
              ass.target.phrase == phrase):
            return inst2, inst1, ass

    raise ModelException("Unknown association %s---(%s.'%s')---%s" % (kind1,
                                                                      rel_id,
                                                                      phrase,
                                                                      kind2))


def _deferred_association_operation(inst, end, op):
    '''
    Generate list of deferred operations which needs to be invoked after an 
    update to identifying attributes on the association end point is made.
    '''
    kind = inst.__class__.__name__
    l = list()
    for ass in chain(*inst.__r__.values()):
        if kind != ass.target.kind:
            continue
        if not set(end.ids) & inst.__d__ - inst.__i__ & set(ass.target.ids):
            # TODO: what about attributes which are both identifying, and referential?
            continue

        nav = navigate_many(inst).nav(ass.source.kind, ass.id, ass.source.phrase)
        for from_inst in nav():
            fn = partial(op, from_inst, inst, ass.id, ass.target.phrase)
            l.append(fn)

    return l


def navigate_one(inst):
    '''
    Initialize a navigation which is modeled as a one-to-one association.
    
    Return value will be an instance or None.
    '''
    return navigate_any(inst)


def navigate_any(inst_or_set):
    '''
    Initialize a navigation which is modeled as a one-to-many or many-to-many
    association and reduce the set to a single instance. 
    
    Return value will be an instance, or None.
    '''
    return NavChain(inst_or_set, is_many=False)


def navigate_many(inst_or_set):
    '''
    Initialize a navigation which is modeled as a one-to-many or many-to-many
    association.
    
    Return value will be a set of instances.
    '''
    return NavChain(inst_or_set, is_many=True)

    
def relate(from_inst, to_inst, rel_id, phrase=''):
    '''
    Relate two instances to each other by copying the identifying attributes
    from the instance on the TO side of a association to the instance on the
    FROM side. Updated values which affect existing associations are 
    propagated.
    
    **NOTE**: Reflexive associations require a phrase, and that the order 
    amongst the instances is as intended.
    '''
    if None in [from_inst, to_inst]:
        return False
    
    from_inst, to_inst, ass = _find_association_links(from_inst, to_inst, rel_id, phrase)
    post_process = _deferred_association_operation(from_inst, ass.source, relate)

    updated = False
    for from_name, to_name in zip(ass.source.ids, ass.target.ids):
        if _is_null(to_inst, to_name):
            raise ModelException('undefined referential attribute %s' % to_name)
        
        from_value = getattr(from_inst, from_name)
        to_value = getattr(to_inst, to_name)

        if from_value == to_value:
            continue

        if not _is_null(from_inst, from_name):
            raise ModelException('instance is already related')
        
        updated = True
        setattr(from_inst, from_name, to_value)

    if updated:
        for deferred_relate in post_process:
            deferred_relate()

    return updated


def unrelate(from_inst, to_inst, rel_id, phrase=''):
    '''
    Unrelate two instances from each other by reseting the identifying
    attributes on the FROM side of the association.
    
    **NOTE**: Reflexive associations require a phrase, and that the order amongst
    the instances is as intended.
    '''
    if None in [from_inst, to_inst]:
        return False
    
    from_inst, to_inst, ass = _find_association_links(from_inst, to_inst, rel_id, phrase)
    post_process = _deferred_association_operation(from_inst, ass.source, unrelate)

    updated = False
    for from_name in set(ass.source.ids) & from_inst.__d__ - from_inst.__i__:
        if _is_null(from_inst, from_name):
            raise ModelException('instances not related')
        
        updated = True
        setattr(from_inst, from_name, None)

    if updated:
        for deferred_unrelate in post_process:
            deferred_unrelate()
        
    return updated

