|Latest Version| |Supported Python Versions| |License|

``bilibili-feedgen`` generates an Atom feed for videos uploaded by a Bilibili user.

.. contents::

Installation
------------

Python 3.6 or later is required (due to `PEP 498 <https://docs.python.org/3.6/whatsnew/3.6.html#whatsnew36-pep498>`_). To install, run ::

  ./setup.py install

or ::

  ./setup.py develop

for continued development. Installation within a virtualenv is highly recommended.

Usage
-----

Basic usage::

  bilibili-feedgen -o 1315101.atom 1315101

For more options, see ::

  bilibili-feedgen -h

Notes
-----

- ``bilibili-feedgen`` taps into Bilibili's private API to retrieve
  video listings. As such, it might break at any time.

License
-------

Copyright (c) 2016 Zhiming Wang <zmwangx@gmail.com>

This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2, as
published by Sam Hocevar. See `COPYING <COPYING>`_ for details.

There is ABSOLUTELY NO WARRANTY.

See Also
--------
`you-get <https://github.com/soimort/you-get>`_.


.. |Latest Version| image:: https://img.shields.io/github/release/zmwangx/bilibili-feedgen.svg?maxAge=3600
   :target: https://github.com/zmwangx/bilibili-feedgen/releases/latest
.. |Supported Python Versions| image:: https://img.shields.io/badge/python-3.6-blue.svg?maxAge=2592000
.. |License| image:: https://img.shields.io/badge/license-WTFPL-blue.svg?maxAge=2592000
   :target: COPYING
