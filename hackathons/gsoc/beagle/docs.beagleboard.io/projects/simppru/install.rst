Install
=======

Dependencies
------------

-  gcc-pru
-  gnuprumcu
-  config-pin utility (for autoconfig)

Installation
------------

For Instructions head over to
`Installation <https://simppru.readthedocs.io/en/latest/install/install/>`__

Requirements
------------

Currently this only supports am335x systems: PocketBeagle, BeagleBone
Black and BeagleBone Black Wireless:

-  ``gcc-pru``
-  ``gnuprumcu``
-  beaglebone image with official support for remoteproc:
   ``ti-4.19+ kernel``
-  ``config-pin`` utility

Build from source
-----------------

For Instructions head over to `Building from
source <https://simppru.readthedocs.io/en/latest/install/build/>`__

   .. code:: bash

      simppru-console

   For detailed usage head to `Detailed
   Usage <https://simppru.readthedocs.io/en/latest/usage/usage-simppru-console>`__

amd64
-----

.. code:: bash

   wget https://github.com/VedantParanjape/simpPRU/releases/download/1.4/simppru-1.4-amd64.deb

   sudo dpkg -i simppru-1.4-amd64.deb

armhf
-----

.. code:: bash

   wget https://github.com/VedantParanjape/simpPRU/releases/download/1.4/simppru-1.4-armhf.deb

   sudo dpkg -i simppru-1.4-armhf.deb

Issues
------

-  For full source code of simPRU
   `visit <https://github.com/VedantParanjape/simppru>`__
-  To report a bug or start a issue
   `visit <https://github.com/VedantParanjape/simppru/issues>`__