.. _capes:

Capes
#####

.. note::
   This page is under development.

.. todo::

   Get OSHWA certification for all of our capes and update the documentation to reflect that

.. admonition:: Contributors

    This work is licensed under a `Creative Commons Attribution-ShareAlike
    4.0 International License <http://creativecommons.org/licenses/by-sa/4.0/>`__

.. note::
    Make sure to read and accept all the terms & condition provided in the :ref:`boards-terms-and-conditions` page. 
    
    Use of either the boards or the design materials constitutes agreement to the T&C including any 
    modifications done to the hardware or software solutions provided by beagleboard.org foundation.

Capes are add-on boards for BeagleBone or PocketBeagle families of boards.  Using a Cape add-on board, you can easily add
sensors, communication peripherals, and more.

Please visit `BeagleBoard.org - Cape <https://beagleboard.org/capes>`_ for the list of currently available Cape add-on boards.

In the BeagleBone board family, there are many variants, such as :ref:`beagleboneblack-home`, :ref:`bbai-home`,
:ref:`bbai64-home` and compatibles such as `SeeedStudio BeagleBone Green <https://beagleboard.org/green>`_,
`SeeedStudio BeagleBone Green Wireless <https://beagleboard.org/green-wireless>`_, `SeeedStudio BeagleBone Green Gateway
<https://wiki.seeedstudio.com/BeagleBone-Green-Gateway/>`_ and more.

The :ref:`beaglebone-cape-interface-spec` enables a common set of device tree overlays and software to be utilized
on each of these different BeagleBone boards.

Each hardware has different internal pin assignments 
and the number of peripherals in the SoC, but the device tree overlay absorbs these differences.

The user of the Cape add-on boards are essentially able to use it 
across the corresponding Boards without changing any code at all.

Find the instructions below on using each cape:

* :ref:`bone-cape-relay`
* :ref:`industrial-comms-cape`

.. toctree::
   :maxdepth: 2
   :hidden:

   cape-interface-spec
   relay
   comms
   motor_cape

