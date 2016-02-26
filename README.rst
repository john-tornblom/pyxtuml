pyxtuml |Build Status| |Coverage Status|
========================================

pyxtuml is a python library for parsing, manipulating, and generating
`BridgePoint <https://www.xtuml.org>`__ xtUML models.

.. sectnum::

============
Dependencies
============

For people running Ubuntu, all dependencies are available via apt-get:

::

   $ sudo apt-get install python2.7 python-ply

pyxtuml also works with python3 and `pypy <http://pypy.org>`__.

============
Installation
============

Install from pypi:

::

    $ python -m pip install pyxtuml

Or fetch the source from github:

::

    $ git clone https://github.com/xtuml/pyxtuml.git
    $ cd pyxtuml
    $ python setup.py install
   
Optionally, you can also execute a test suite:

::

    $ python setup.py test

=============
Usage example
=============

The `examples
folder <https://github.com/xtuml/pyxtuml/tree/master/examples>`__
contains a few scripts which demonstrate how pyxtuml may be used.

The following command will create an empty metamodel and populate it
with some sample data:

::

    $ python examples/create_external_entity.py > test.sql

Copy the SQL statements saved in test.sql to your clipboard, and paste
them into the BridgePoint editor with a project selected in the project
explorer.

If you are on a more recent GNU/Linux system, you can also pipe the
output directly to your clipboard without bouncing via disk:

::

    $ python examples/create_external_entity.py | xclip -selection clipboard

==================
Command Line Tools
==================

pyxtuml contain a few useful command line tools which are described below.

Check model for integrity violations
------------------------------------
A model may be checked for association constraint violations. By default, all 
associations are checked. Optionally, the check may be limited to one or more 
associations by appending the -r argument for each association to check.

::

   $ python -m xtuml.consistency_check [options] <sql_file> [another_sql_file...]

Using the above command, both the model and schema needs to be provided by the user. 
If the model is expressed in the bridgepoint meta model (ooaofooa), the following
command may be used instead:

::

   $ python -m bridgepoint.consistency_check [options] <model_path> [another_model_path...]

With this command, the user only have to provide the model (the models folder 
containing all .xtuml files).

**Available options**

--help, -h   show this help message and exit
--version    show program's version number and exit
-r <number>  limit consistency check to one or more associations
-v           increase debug logging level

Generate a meta model schema
----------------------------
To create an sql schema from a bridgepoint model, the following command may be used:

::

   $ python -m bridgepoint.gen_sql_schema [options] <model_path> [another_model_path...]

**Available options**

--help, -h  show this help message and exit
--version   show program's version number and exit
-c NAME     export sql schema for the component named NAME
-o PATH     save sql schema to PATH (required)
-v          increase debug logging level

Generate an xsd schema
----------------------
To create an xsd schema for xml files, the following command may be used:

::

   $ python -m bridgepoint.gen_xsd_schema [options] <model_path> [another_model_path...]

**Available options**

--help, -h  show this help message and exit
--version   show program's version number and exit
-c NAME     export xsd schema for the component named NAME
-o PATH     save xsd schema to PATH (required)
-v          increase debug logging level

Note that the schema is compatible with Microsoft Excel. Consequently, Excel 
may be used to define instances in a model that can be easily exported to xml
files. 

Object Action Language Prebuilder
---------------------------------
Generally, all model compilers takes as input an sql where all OAL actions
has been translated from its textual representation into instances in the 
ooaofooa meta model. This translation is usually conducted by the Eclipse-
based prebuilder included with the BridgePoint IDE. pyxtuml contains an 
independent prebuilder, implemented in python (and thus may be somewhat 
slower). The pyxtuml prebuilder may be invoked using the folling command:

::

   $ python -m bridgepoint.prebuild [options] <model_path> [another_model_path..]

**Available options**

--help, -h  show this help message and exit
--version   show program's version number and exit¨
-o PATH     set output to PATH
-v          increase debug logging level

==============
Reporting bugs
==============

If you encounter problems with pyxtuml, please `file a github
issue <https://github.com/xtuml/pyxtuml/issues/new>`__. If you
plan on sending pull request which affect more than a few lines of code,
please file an issue before you start to work on you changes. This will
allow us to discuss the solution properly before you commit time and
effort.

=======
License
=======

pyxtuml is licensed under the GPLv3, see LICENSE for more information.

.. |Build Status| image:: https://travis-ci.org/xtuml/pyxtuml.svg?branch=master
   :target: https://travis-ci.org/xtuml/pyxtuml
.. |Coverage Status| image:: https://coveralls.io/repos/xtuml/pyxtuml/badge.svg?branch=master
   :target: https://coveralls.io/r/xtuml/pyxtuml?branch=master
