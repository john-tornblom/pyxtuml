pyxtuml
========
pyxtuml is a python library for parsing, manipulating, and generating [BridgePoint](https://www.xtuml.org) xtUML models. The library operates at the metamodel, hence you cannot execute models using only pyxtuml. However, the action language (OAL) may be parsed and tranlated into a syntax tree by pyxtuml.

### Getting Started
pyxtuml depend on the following software packages:
* [python](http://python.org) (tested with v2.7)
* [ply](http://www.dabeaz.com/ply) (tested with v3.4)
* [antlr2](http://www.antlr2.org) (tested with v2.7.7) _optional_

For people running Ubuntu 14.04, all packages are available via apt-get.
```
$ sudo apt-get install python2.7 python-ply antlr python-antlr
```

Once the dependencies have been met, the source code needs to be prepared by issuing the following set of commands.
```
$ git clone https://github.com/john-tornblom/pyxtuml.git
$ cd pyxtuml
$ python setup.py prepare
```

There is an test script located in the example folder, which demonstrates how one could define new external entities using pyxtuml. To test it, just type
```
$ python examples/create_external_entity.py > test.sql
```

Copy the SQL statements saved to test.sql, and paste them into the BridgePoint editor with a project selected in the project explorer.

### License
pyxtuml is licensed under the GPLv3, see LICENSE for more information.
