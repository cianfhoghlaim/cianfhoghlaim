Build from source
=================

Dependencies
------------

-  flex
-  bison
-  gcc
-  gcc-pru
-  gnuprumcu
-  cmake

Build
-----

.. code:: bash

   git clone https://github.com/VedantParanjape/simpPRU.git
   cd simpPRU
   mkdir build
   cd build
   cmake ..
   make 

Install
-------

.. code:: bash

   sudo make install

Generate debian package
-----------------------

.. code:: bash

   sudo make package
