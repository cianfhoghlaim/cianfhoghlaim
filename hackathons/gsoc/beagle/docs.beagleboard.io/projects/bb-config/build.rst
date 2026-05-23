Build from Source
###################

Dependencies
**************

-  g++
-  cmake
-  glib-2.0
-  libnm

Build
******

.. code:: bash

   git clone https://git.beagleboard.org/gsoc/bb-config
   cd bb-config
   mkdir build
   cd build
   cmake ..
   make -j$(nproc)

Install
********

.. code:: bash

   sudo make install
