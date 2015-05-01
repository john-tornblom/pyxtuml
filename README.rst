pyxtuml |Build Status| |Coverage Status|
========================================

pyxtuml is a python library for parsing, manipulating, and generating
`BridgePoint <https://www.xtuml.org>`__ xtUML models.

Dependencies
~~~~~~~~~~~~

For people running Ubuntu, all dependencies are available via apt-get:

::

   $ sudo apt-get install python2.7 python-ply
   

   
Installation
~~~~~~~~~~~~

Install from pypi:

::

    $ python -m pip install pyxtuml

Or fetch the source from github:

::

    $ git clone https://github.com/john-tornblom/pyxtuml.git
    $ cd pyxtuml
    $ python setup.py prepare
    $ python setup.py install
   
Optionally, you can also execute a test suite:

::

    $ python setup.py test


Usage example
~~~~~~~~~~~~~
The `examples
folder <https://github.com/john-tornblom/pyxtuml/tree/master/examples>`__
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

Reporting bugs
~~~~~~~~~~~~~~
If you encounter problems with pyxtuml, please `file a github
issue <https://github.com/john-tornblom/pyxtuml/issues/new>`__. If you
plan on sending pull request which affect more than a few lines of code,
please file an issue before you start to work on you changes. This will
allow us to discuss the solution properly before you commit time and
effort.

License
~~~~~~~
pyxtuml is licensed under the GPLv3, see LICENSE for more information.

.. |Build Status| image:: https://travis-ci.org/john-tornblom/pyxtuml.svg?branch=master
   :target: https://travis-ci.org/john-tornblom/pyxtuml
.. |Coverage Status| image:: https://coveralls.io/repos/john-tornblom/pyxtuml/badge.svg?branch=master
   :target: https://coveralls.io/r/john-tornblom/pyxtuml?branch=master
