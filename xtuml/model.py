# encoding: utf-8
# Copyright (C) 2016 John Törnblom

from itertools import chain
from functools import partial

import logging
import collections

try:
    from future_builtins import filter, zip
except ImportError:
    pass

import xtuml


logger = logging.getLogger(__name__)


class ModelException(Exception):
    '''
    Base class for all pyxtuml-specific exceptions 
    '''


class UnknownClassException(ModelException):
    pass


class UnknownAssociationException(ModelException):

    def __init__(self, from_kind, to_kind, rel_id, phrase):
        if phrase:
            msg = "%s->%s[%s, %s]" % (from_kind, to_kind, repr(rel_id), repr(phrase))
        else:
            msg = "%s->%s[%s]" % (from_kind, to_kind, repr(rel_id))

        ModelException.__init__(self, msg)


class NavChain(object):
    '''
    A navigation chain initializes a query from one or more instances.
    Queries may be syntactically cascaded in several ways:
    
       res = NavChain(inst).nav('X', 'R100', 'phrase').nav('Y', 101)

    or using an OAL/RSL inspired syntax:
    
       res = NavChain(inst).X[100, 'phrase'].Y[101](lamda x: <filter expression>)
    '''
    
    def __init__(self, handle):
        if handle is None:
            handle = []
            
        elif isinstance(handle, BaseObject):
            handle = [handle]
        
        elif not isinstance(handle, collections.Iterable):
            raise ModelException("Unable to navigate across '%s'" % type(handle))
        
        self.handle = handle
        self._kind = None
        
    def nav(self, kind, relid, phrase=''):
        self.handle = NavChain._nav(self.handle, kind, relid, phrase)
        return self
    
    @staticmethod
    def _nav(handle, kind, rel_id, phrase):
        kind = kind.upper()
        if isinstance(rel_id, int):
            rel_id = 'R%d' % rel_id
    
        for inst in iter(handle):
            for result in inst.__metaclass__.navigate(inst, kind, rel_id, phrase):
                yield result
            
    def __getattr__(self, name):
        self._kind = name
        return self
    
    def __getitem__(self, args):
        if not isinstance(args, tuple):
            args = (args, '')
        
        relid, phrase = args
        
        return self.nav(self._kind, relid, phrase)


class NavOneChain(NavChain):
    
    def __call__(self, where_clause=None):
        handle = self.handle or iter([])
        if not where_clause:
            return next(handle, None)
        
        for inst in handle:
            if where_clause(inst):
                return inst


class NavManyChain(NavChain):
    
    def __call__(self, where_clause=None):
        handle = self.handle or list()
        return QuerySet(filter(where_clause, handle))


class Link(object):
    
    def __init__(self, from_metaclass, rel_id, to_metaclass, phrase, key_map):
        if isinstance(rel_id, int):
            rel_id = 'R%d' % rel_id
        
        self.rel_id = rel_id
        self.from_metaclass = from_metaclass
        self.to_metaclass = to_metaclass
        self.phrase = phrase
        self.key_map = key_map
        
    @property
    def kind(self):
        return self.to_metaclass.kind

    def navigate(self, inst):
        kwargs = dict()
        for key, mapped_key in self.key_map:
            kwargs[mapped_key] = getattr(inst, key)

        return self.to_metaclass.query(kwargs)
        
    def __repr__(self):
        if self.phrase:
            return "%s->%s[%s, %s]" % (self.kind, self.to_metaclass.kind, 
                                       repr(self.rel_id), repr(self.phrase))
        else:
            return "%s->%s[%s]" % (self.kind, self.to_metaclass.kind, 
                                   repr(self.rel_id))


class ReversedLink(Link):
    
    def __init__(self, from_metaclass, rel_id, to_metaclass, phrase, key_map):
        key_map = [(key2, key1) for key1, key2 in key_map]
        Link.__init__(self, from_metaclass, rel_id, to_metaclass, phrase, key_map)


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
        return self.source.kind.upper() == self.target.kind.upper()

    
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
    An ordered set which holds instances that match queries from a metamodel.
    '''
    
    @property
    def first(self):
        if len(self):
            return next(iter(self))
    
    @property
    def last(self):
        if len(self):
            return next(reversed(self))


class Query(object):
    result = None
    generator = None
    
    def __init__(self, table, kwargs):
        self.result = collections.deque()
        self.items = collections.deque(kwargs.items())
        self.table = table
        self.generator = self.mk_generator()
        
    def mk_generator(self):
        for inst in iter(self.table):
            for name, value in iter(self.items):
                if getattr(inst, name) != value or _is_null(inst, name):
                    break
            else:
                self.result.append(inst)
                yield inst
    
        self.generator = None
    
    def execute(self):
        for inst in self.result:
            yield inst
            
        while self.generator:
            yield next(self.generator)
        
        
class BaseObject(object):
    '''
    A common base object for all instances created in a metamodel. Accesses 
    to attributes, e.g. getattr/setattr, on these objects are case insensitive.
    '''
    def __init__(self):
        self.__metaclass__.cache.clear()
        
    def __add__(self, other):
        assert isinstance(other, BaseObject)
        return QuerySet([self, other])

    def __sub__(self, other):
        assert isinstance(other, BaseObject)
        if self == other: return QuerySet()
        else: return QuerySet([self])

    def __getattr__(self, name):
        uname = name.upper()
        for attr, _ in self.__metaclass__.attributes:
            if attr.upper() == uname:
                return self.__dict__[attr]

        return object.__getattribute__(self, name)
    
    def __setattr__(self, name, value):
        uname = name.upper()
        for attr, _ in self.__metaclass__.attributes:
            if attr.upper() == uname:
                self.__dict__[attr] = value
                self.__metaclass__.cache.clear()
                return

        self.__dict__[name] = value
        
    def __str__(self):
        return str(self.__dict__)


class MetaClass(object):
    metamodel = None
    kind = None
    attributes = None
    referential_attributes = None
    identifying_attributes = None
    links = None
    indices = None
    clazz = None
    instances = None
    cache = None
    
    def __init__(self, kind, metamodel=None):
        self.metamodel = metamodel
        self.kind = kind
        self.attributes = list()
        self.referential_attributes = set()
        self.identifying_attributes = set()
        self.indices = dict()
        self.links = dict()
        self.instances = list()
        self.cache = dict()
        self.clazz = type(kind, (BaseObject,), dict(__metaclass__=self))
        
    def __call__(self, *args, **kwargs):
        return self.new(*args, **kwargs)
        
    @property
    def attribute_names(self):
        return [name for name, _ in self.attributes]
    
    def add_link(self, metaclass, rel_id, phrase, key_map, reverse=False):
        if isinstance(rel_id, int):
            rel_id = 'R%d' % rel_id
        
        if reverse:
            link = ReversedLink(self, rel_id, metaclass, phrase, key_map)
        else:
            link = Link(self, rel_id, metaclass, phrase, key_map)
            
        key = (metaclass.kind, rel_id, phrase)
        self.links[key] = link
        
    def find_link(self, kind, rel_id, phrase):
        if isinstance(rel_id, int):
            rel_id = 'R%d' % rel_id
            
        key = (kind, rel_id, phrase)
        return self.links.get(key, None)
        
    def append_attribute(self, name, ty):
        attr = (name, ty)
        self.attributes.append(attr)
        setattr(self.clazz, name, None)
        
    def insert_attribute(self, index, name, ty):
        attr = (name, ty)
        self.attributes.insert(index, attr)
        setattr(self.clazz, name, None)
        
    def delete_attribute(self, name):
        for idx, attr in enumerate(self.attributes):
            attr_name, _ = attr
            if attr_name == name:
                del self.attributes[idx]
                return
        
    def default_value(self, type_name):
        uname = type_name.upper()
        if   uname == 'BOOLEAN':
            return False
            
        elif uname == 'INTEGER':
            return 0
            
        elif uname == 'REAL':
            return 0.0
            
        elif uname == 'STRING':
            return ''
            
        elif uname == 'UNIQUE_ID':
            if self.metamodel:
                return next(self.metamodel.id_generator)
            else:
                return None
        else:
            raise ModelException("Unknown type named '%s'" % type_name)
        
    def new(self, *args, **kwargs):
        inst = self.clazz()
        
        # set all attributes with an initial default value
        for name, ty in self.attributes:
            if name in self.referential_attributes:
                value = None
            else:
                value = self.default_value(ty)
            setattr(inst, name, value)
            
        # set all positional arguments
        for attr, value in zip(self.attributes, args):
            name, ty = attr
            setattr(inst, name, value)
            
        # set all named arguments
        for name, value in kwargs.items():
            setattr(inst, name, value)
            
        self.instances.append(inst)
        
        return inst

    def delete(self, inst):
        if inst in self.instances:
            self.instances.remove(inst)
            self.cache.clear()
        else:
            raise ModelException("Instance not found in its model")

    def select_one(self, where_clause=None):
        if isinstance(where_clause, dict):
            s = self.query(where_clause)
        else:
            s = iter(filter(where_clause, self.instances))
            
        return next(s, None)

    def select_many(self, where_clause=None):
        if isinstance(where_clause, dict):
            s = self.query(where_clause)
        else:
            s = filter(where_clause, self.instances)
        
        return QuerySet(s)

    def navigate(self, inst, kind, rel_id, phrase=''):
        key = (kind, rel_id, phrase)
        if key in self.links:
            link = self.links[key]
            return link.navigate(inst)
        else:
            raise UnknownAssociationException(self.kind, kind, rel_id, phrase)
            
    def query(self, kwargs):
        index = frozenset(list(kwargs.items()))
        if index not in self.cache:
            self.cache[index] = Query(self.instances, kwargs)
            
        return self.cache[index].execute()


def _is_null(inst, name):
    value = getattr(inst, name)
    if value:
        return False
    
    elif value is None:
        return True

    name = name.upper()
    for attr_name, attr_ty in inst.__metaclass__.attributes:
        if attr_name.upper() != name:
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
    A metamodel contains class definitions with associations between them,
    and instances of different kinds of classes.
    
    **Note:** All identifiers, e.g. attributes, association ids, key letters 
    (the kind or name of a class), are case **insensitive**.
    '''
    metaclasses = None
    associations = None
    id_generator = None
    
    def __init__(self, id_generator=None):
        '''
        Create a new, empty metamodel. 
        Optionally, specify an id generator used to obtain unique identifiers.
        '''
        if id_generator is None:
            id_generator = xtuml.UUIDGenerator()
        
        self.metaclasses = dict()
        self.associations = list()
        self.id_generator = id_generator
    
    @property
    def instances(self):
        for metaclass in self.metaclasses.values():
            for inst in metaclass.instances:
                yield inst
    
    @property
    def classes(self):
        for metaclass in self.metaclasses.values():
            yield metaclass.clazz
    
    def define_class(self, kind, attributes, doc=''):
        '''
        Define a new class in the metamodel, and return its metaclass.
        '''
        ukind = kind.upper()
        if ukind in self.metaclasses:
            raise ModelException('A class with the name %s is already defined' % kind)

        metaclass = MetaClass(kind, self)
        for name, ty in attributes:
            metaclass.append_attribute(name, ty)
            
        self.metaclasses[ukind] = metaclass
        
        return metaclass

    def find_class(self, kind):
        '''
        Find a class of some *kind* in the metamodel.
        '''
        return self.find_metaclass(kind).clazz

    def find_metaclass(self, kind):
        '''
        Find a metaclass of some *kind* in the metamodel.
        '''
        ukind = kind.upper()
        if ukind in self.metaclasses:
            return self.metaclasses[ukind]
        else:
            raise UnknownClassException(kind)

    def new(self, kind, *args, **kwargs):
        '''
        Create and return a new instance in the metamodel of some *kind*.
        
        Optionally, initial attribute values may be assigned to the new instance
        by passing them as positional or keyword arguments. Positional arguments
        are assigned in the order in which they appear in the metamodel schema.
        '''
        metaclass = self.find_metaclass(kind)
        return metaclass.new(*args, **kwargs)
        
    def clone(self, instance):
        '''
        Create a shallow clone of an *instance*.
        
        **Note:** the clone and the original instance **does not** have to be
        part of the same metamodel. 
        '''
        clone = self.new(instance.__metaclass__.kind)
        for name, _ in instance.__metaclass__.attributes:
            value = getattr(instance, name)
            setattr(clone, name, value)
            
        return clone
        
    def define_relation(self, rel_id, source, target):
        '''
        This method is deprecated. Use *define_association* instead.
        '''
        return self.define_association(rel_id, source, target)
    
    def define_association(self, rel_id, source, target):
        '''
        Define and return an association between *source* to *target* named 
        *rel_id*.
        '''
        source_metaclass = self.find_metaclass(source.kind)
        target_metaclass = self.find_metaclass(target.kind)
        
        key_map = list(zip(source.ids, target.ids))
        source_metaclass.add_link(target_metaclass, rel_id, target.phrase, key_map)
        target_metaclass.add_link(source_metaclass, rel_id, source.phrase, key_map, reverse=True)
        
        source_metaclass.referential_attributes |= set(source.ids)
        target_metaclass.identifying_attributes |= set(target.ids)
        
        ass = Association(rel_id, source, target)
        self.associations.append(ass)
        
        return ass
        
    def define_unique_identifier(self, kind, name, *named_attributes):
        '''
        Define a unique identifier for some *kind* of class based on its *named attributes*
        '''
        if not named_attributes:
            return
        
        if isinstance(name, int):
            name = 'I%d' % name
        
        metaclass = self.find_metaclass(kind)
        metaclass.indices[name] = set(named_attributes)

    def select_many(self, kind, where_clause=None):
        '''
        Query the metamodel for a set of instances of some *kind*. Optionally,
        a conditional *where-clause* in the form of a function may be provided.
        
        Usage example:
        
        >>> m = xtuml.load_metamodel('db.sql')
        >>> inst_set = m.select_many('My_Class', lambda sel: sel.number > 5)
        '''
        metaclass = self.find_metaclass(kind)
        return metaclass.select_many(where_clause)
    
    def select_any(self, kind, where_clause=None):
        '''
        This method is deprecated. Use *select_one* instead.
        '''
        return self.select_one(kind, where_clause)
    
    def select_one(self, kind, where_clause=None):
        '''
        Query the model for a single instance of some *kind*. Optionally, a
        conditional *where-clause* in the form of a function may be provided.
        
        Usage example:
        
        >>> m = xtuml.load_metamodel('db.sql')
        >>> inst = m.select_one('My_Class', lambda sel: sel.name == 'Test')
        '''
        metaclass = self.find_metaclass(kind)
        return metaclass.select_one(where_clause)
        
    def is_consistent(self):
        '''
        Check the model for integrity violations.
        '''
        if not xtuml.check_association_integrity(self):
            return False
        
        return xtuml.check_uniqueness_constraint(self)
    
    def _select_endpoint(self, inst, source, target, kwargs):
        metaclass = self.find_metaclass(target.kind)
        keys = chain(target.ids, kwargs.keys())
        values = chain([getattr(inst, name) for name in source.ids],
                       kwargs.values())
        kwargs = dict(zip(keys, values))

        return metaclass.query(kwargs)

    def _formalized_query(self, source, target):
        return lambda inst, **kwargs: self._select_endpoint(inst, source,
                                                            target, kwargs)
    

def navigate_one(instance):
    '''
    Initialize a navigation from one *instance* to another across a one-to-one
    association.
    
    The resulting query will return an instance or None.
    
    Usage example:
    
    >>> from xtuml import navigate_one as one
    >>> m = xtuml.load_metamodel('db.sql')
    >>> inst = m.select_any('My_Modeled_Class')
    >>> other_inst = one(inst).Some_Other_Class[4]()
    
    The syntax is somewhat similar to the action language used in BridgePoint.
    The same semantics would be expressed in BridgePoint as::
    
        select any inst from instances of My_Modeled_Class;
        select one other_inst related by inst->Some_Other_Class[R4];
    
    **Note:** If the navigated association is reflexive, a phrase must be 
    provided, e.g.
    
    >>> other_inst = one(inst).Some_Other_Class[4, 'some phrase']()
    '''
    return navigate_any(instance)


def navigate_any(instance_or_set):
    '''
    Initialize a navigation from an instance, or a set of instances, to 
    associated instances across a one-to-many or many-to-many association.

    The resulting query will return an instance or None.
    '''
    return NavOneChain(instance_or_set)


def navigate_many(instance_or_set):
    '''
    Initialize a navigation from an instance, or a set of instances, to 
    associated instances across a one-to-many or many-to-many association.
    
    The resulting query will return a set of instances.
    '''
    return NavManyChain(instance_or_set)


def navigate_subtype(supertype, rel_id):
    '''
    Perform a navigation from *supertype* to its subtype across *rel_id*. The
    navigated association must be modeled as a subtype-supertype association.
    
    The return value will an instance or None.
    '''
    if not supertype:
        return
    
    if isinstance(rel_id, int):
        rel_id = 'R%d' % rel_id

    for kind, rel_id_candidate, _ in supertype.__metaclass__.links:
        if rel_id != rel_id_candidate:
            continue
        
        subtype = navigate_one(supertype).nav(kind, rel_id)()
        if subtype:
            return subtype


def sort_reflexive(set_of_instances, rel_id, phrase):
    '''
    Sort a *set of instances* in the order they appear across a conditional and
    reflexive association. The first instance in the resulting ordered set is
    **not** associated to an instance across the given *phrase*.
    '''
    if (not isinstance(set_of_instances, QuerySet) or 
        not set_of_instances.first):
        return QuerySet()
    
    if isinstance(rel_id, int):
        rel_id = 'R%d' % rel_id
    
    # Figure out the phrase in the other direction
    metaclass = set_of_instances.first.__metaclass__
    for link in metaclass.links.values():
        if link.to_metaclass != metaclass:
            continue
        
        if link.rel_id != rel_id:
            continue

        if link.phrase == phrase:
            continue

        other_phrase = link.phrase
        break
    else:
        raise UnknownAssociationException(metaclass.kind, rel_id, phrase)
    

    first_filt = lambda sel: not navigate_one(sel).nav(metaclass.kind, rel_id, phrase)()
    first_instances = list(filter(first_filt, set_of_instances))
    if not first_instances:
        #the instance sequence is recursive, start anywhere
        first_instances = [set_of_instances.first]
    
    def sequence_generator():
        for first in first_instances:
            inst = first
            while inst:
                yield inst
                inst = navigate_one(inst).nav(metaclass.kind, rel_id, other_phrase)()
                if inst is first:
                    break
                
    return QuerySet(sequence_generator())

    
def _find_link(inst1, inst2, rel_id, phrase):
    metaclass1 = inst1.__metaclass__
    metaclass2 = inst2.__metaclass__

    link = metaclass2.find_link(metaclass1.kind, rel_id, phrase)
    if link and not isinstance(link, ReversedLink):
        return inst2, inst1, link
        
    link = metaclass1.find_link(metaclass2.kind, rel_id, phrase)
    if link and not isinstance(link, ReversedLink):
        return inst1, inst2, link

    if isinstance(rel_id, int):
        rel_id = 'R%d' % rel_id
        
    for other_link in metaclass1.links.values():
        if other_link == link:
            continue
        
        if other_link.to_metaclass != metaclass1:
            continue
        
        if other_link.rel_id != rel_id:
            continue

        if other_link.phrase == phrase:
            continue

        return inst1, inst2, other_link
        
    raise UnknownAssociationException(metaclass1.kind, metaclass2.kind,
                                      rel_id, phrase)
                                          

def _deferred_link_operation(inst, link, op):
    '''
    Generate list of deferred operations which needs to be invoked after an 
    update to identifying attributes on the association end point is made.
    '''
    l = list()
    
    metaclass = inst.__metaclass__
    keys = set([key for key, _ in link.key_map])
    for link in metaclass.links.values():
        if not isinstance(link, ReversedLink):
            continue
        
        derived_keys = set([key for key, _ in link.key_map])
        if not (keys & derived_keys):
            continue
        
        nav = navigate_many(inst).nav(link.to_metaclass.kind, link.rel_id, link.phrase)
        for from_inst in nav():
            fn = partial(op, from_inst, inst, link.rel_id, link.phrase)
            l.append(fn)

    return l

    
def relate(from_instance, to_instance, rel_id, phrase=''):
    '''
    Relate *from_instance* to *to_instance* across *rel_id*. For refelxive
    association, a *phrase* indicating the direction must also be provided.
    
    The two instances are related to each other by copying the identifying 
    attributes from the instance on the TO side of a association to the instance
    n the FROM side. Updated values which affect existing associations are 
    propagated.
    '''
    if None in [from_instance, to_instance]:
        return False
        
    from_instance, to_instance, link = _find_link(from_instance, to_instance,
                                                  rel_id, phrase)
                                                      
    post_process = _deferred_link_operation(from_instance, link, relate)
    updated = False
    
    for from_name, to_name in link.key_map:
        if _is_null(to_instance, to_name):
            raise ModelException('undefined referential attribute %s' % to_name)
        
        from_value = getattr(from_instance, from_name)
        to_value = getattr(to_instance, to_name)

        if from_value == to_value:
            continue

        if not _is_null(from_instance, from_name):
            raise ModelException('instance is already related')
        
        updated = True
        setattr(from_instance, from_name, to_value)

    if updated:
        for deferred_relate in post_process:
            deferred_relate()

    return updated


def unrelate(from_instance, to_instance, rel_id, phrase=''):
    '''
    Unrelate *from_instance* from *to_instance* across *rel_id*. For refelxive
    association, a *phrase* indicating the direction must also be provided.
    
    The two instances are unrelated from each other by reseting the identifying
    attributes on the FROM side of the association. Updated values which affect
    existing associations are propagated.
    '''
    if None in [from_instance, to_instance]:
        return False
    
    from_instance, to_instance, link = _find_link(from_instance, to_instance,
                                                  rel_id, phrase)
    post_process = _deferred_link_operation(from_instance, link, unrelate)

    updated = False
    for from_name, _ in link.key_map:
        if _is_null(from_instance, from_name):
            raise ModelException('instances not related')
        
        updated = True
        setattr(from_instance, from_name, None)

    if updated:
        for deferred_unrelate in post_process:
            deferred_unrelate()
        
    return updated


def delete(instance):
    '''
    Delete an *instance* from its metamodel.
    '''
    if not isinstance(instance, BaseObject):
        raise ModelException("not an xtuml instance")
            
    instance.__metaclass__.delete(instance)


class WhereEqual(dict):
    
    def __call__(self, selected):
        for name in self:
            if getattr(selected, name) != self.get(name):
                return False
            
        return True


def where_eq(**kwargs):
    '''
    Return a where-clause which filters out instances based on named 
    keywords.
    
    Usage example:
    
    >>> from xtuml import where_eq as where
    >>> m = xtuml.load_metamodel('db.sql')
    >>> inst = m.select_any('My_Modeled_Class', where(My_Number=5))
    '''
    return WhereEqual(kwargs)

