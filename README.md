pyxtuml		[![Build Status](https://travis-ci.org/john-tornblom/pyxtuml.svg?branch=master)](https://travis-ci.org/john-tornblom/pyxtuml)
========
pyxtuml is a python library for parsing, manipulating, and generating [BridgePoint](https://www.xtuml.org) xtUML models. The library operates at the metamodel, hence you cannot execute models using pyxtuml. 

In addition to reading models, pyxtuml also provides an experimental interpreter for the Rule Specification Language (RSL). RSL is commonly used as a template language to express transformations from a BridgePoint model into a textual representation, e.g. when writing model compilers or when generating html documentation from a model. 

### Getting Started
pyxtuml depend on the following software packages:
* [python](http://python.org) (tested with v2.7)
* [ply](http://www.dabeaz.com/ply) (tested with v3.4)

For people running Ubuntu 14.04, all packages are available via apt-get.
```
$ sudo apt-get install python2.7 python-ply
```

Once the dependencies have been met, the source code needs to be prepared by issuing the following set of commands.
```
$ git clone https://github.com/john-tornblom/pyxtuml.git
$ cd pyxtuml
$ python setup.py prepare
```

Optionally, you can also execute a test suite for the RSL interpreter:
```
$ python setup.py test
```

### Using the RSL interpreter
The usage of the RSL interpreter is as follows:
```
Usage:
  gen_erate.py [OPTION]... {filename}

Options:

	--version               show program's version number and exit
	--help, -h              show this help message and exit
	--import=PATH, -i PATH  import model information from PATH
	--emit=WHEN, -e WHEN    choose when to emit (never, change, always)
	--force, -f             make read-only emit files writable
	--diff=PATH, -d PATH    save a diff of all emits to PATH
	--verbosity, -v         increase debug logging level
```

For example, to execute an RSL template from stdin, just type:
```
$ echo '.print "Hello world!"' | ./gen_erate.py /dev/stdin
```

### Generating models
Rather than using RSL to create or modify a metamodel, you can use python directly. 
This might be useful if you try to import information expressed in some other form, e.g. C/C++ Header files.
For example, one can use [the python binding for clang](https://github.com/llvm-mirror/clang/tree/master/bindings/python) to create external entities from C/C++ header files automatically.

The following command will create an empty metamodel and populate it with some sample data:
```
$ python examples/create_external_entity.py > test.sql
```
Copy the SQL statements saved in test.sql to your clipboard, and paste them into the BridgePoint editor with a project selected in the project explorer.

If you are on a more recent GNU/Linux system, you can also pipe the output directly to your clipboard without bouncing via disk:
```
$ python examples/create_external_entity.py | xclip -selection clipboard
```

Please note that pyxtuml is still regarded as experimental, and its API might change.

### Reporting bugs
If you encounter problems with pyxtuml, please [file a github issue](https://github.com/john-tornblom/pyxtuml/issues/new). 
If you plan on sending pull request which affect more than a few lines of code, please file an issue before you start to work on you changes.
This will allow us to discuss the solution properly before you commit time and effort.

### License
pyxtuml is licensed under the GPLv3, see LICENSE for more information.
