# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
pyxtuml is a python library for parsing, manipulating, and generating
BridgePoint xtUML models.
'''
from . import version

from .tools import IdGenerator
from .tools import UUIDGenerator
from .tools import IntegerGenerator
from .tools import OrderedSet

from .tools import Walker
from .tools import Visitor
from .tools import NodePrintVisitor

from .load import load_metamodel
from .load import ParsingException
from .load import ModelLoader

from .persist import persist_database
from .persist import persist_instances
from .persist import persist_schema

from .persist import serialize_database
from .persist import serialize_schema
from .persist import serialize_class
from .persist import serialize_association
from .persist import serialize_unique_identifiers
from .persist import serialize_instances
from .persist import serialize_instance
from .persist import serialize_value
from .persist import serialize

from xtuml.meta import Association
from xtuml.meta import Link
from xtuml.meta import ReversedLink

from xtuml.meta import QuerySet
from xtuml.meta import Class
from xtuml.meta import BaseObject
from xtuml.meta import MetaClass
from xtuml.meta import MetaModel

from xtuml.meta import MetaException
from xtuml.meta import DeleteException
from xtuml.meta import RelateException
from xtuml.meta import UnrelateException
from xtuml.meta import MetaModelException
from xtuml.meta import UnknownLinkException
from xtuml.meta import UnknownClassException

from xtuml.meta import navigate_any
from xtuml.meta import navigate_one
from xtuml.meta import navigate_many
from xtuml.meta import navigate_subtype
from xtuml.meta import relate
from xtuml.meta import unrelate
from xtuml.meta import delete
from xtuml.meta import where_eq
from xtuml.meta import sort_reflexive

from .consistency_check import check_association_integrity
from .consistency_check import check_uniqueness_constraint




