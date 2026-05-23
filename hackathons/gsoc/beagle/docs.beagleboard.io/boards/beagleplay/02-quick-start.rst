.. _beagleplay-quick-start:

Quick Start Guide
####################

What's included in the box?
****************************

When you purchase a brand new BeaglePlay, In the box you'll get:

1. `BeaglePlay board <https://www.beagleboard.org/boards/beagleplay>`_
2. One (1) sub-GHz antenna
3. Three (3) 2.4GHz/5GHz antennas
4. Plastic standoff hardware
5. Quick-start card

.. tip:: For board files, 3D model, and more, you can checkout `BeaglePlay repository on OpenBeagle <https://openbeagle.org/beagleplay/beagleplay>`_.

.. image:: images/product-pictures/45fontall.*
    :width: 940
    :align: center
    :alt: BeaglePlay box contents

Attaching antennas
******************

You can watch this video to see how to attach the antennas.

.. youtube:: 8zeIVd-JRc0
    :width: 100%
    :align: center

Tethering to PC
****************

.. tip:: 
    Checkout :ref:`beagleboard-getting-started` for,

    1. Updating to latest software.
    2. Power and Boot.
    3. Network connection.
    4. Browsing to your Beagle.
    5. Troubleshooting.

For tethering to your PC you'll need a USB-C data cable.

.. figure:: images/tethered-connection.*
    :width: 1400
    :align: center
    :alt: Tethering BeaglePlay to PC

    Tethering BeaglePlay to PC

Access VSCode
****************

You can access VSCode in two ways:

1. :ref:`beagleplay-usb-vscode`
2. :ref:`beagleplay-access-point-vscode`

.. _beagleplay-usb-vscode:

USB
====

Once connected, you can browse to `192.168.7.2:3000 <http://192.168.7.2:3000>`_ to access the VSCode IDE 
to browse documents and start programming your BeaglePlay!

.. _beagleplay-access-point-vscode:

Access Point
============

By default BeaglePlay Access Point is enabled, You can connect to ``BeaglePlay-XXXX`` Access Point with the password ``BeaglePlay`` and then
browse to `192.168.7.2:3000 <http://192.168.7.2:3000>`_ to access the VSCode IDE.

.. note::

   You may get a warning about an invalid or self-signed certificate. This is a limitation of
   not having a public URL for your board. If you have any questions about this, please as on
   https://forum.beagleboard.org/tag/play.

.. figure:: images/vscode.*
    :width: 1400
    :align: center
    :alt: BeaglePlay VSCode IDE (192.168.7.2:3000)

    BeaglePlay VSCode IDE (192.168.7.2:3000)

.. tip::
     For more Wifi and Access Point related info go to :ref:`beagleplay-connect-wifi`

.. _beagleplay-demos-and-tutorials:

Demos and Tutorials
*******************

* :ref:`beagleplay-serial-console`
* :ref:`beagleplay-connect-wifi`
* :ref:`beagleplay-qwiic`
* :ref:`beagleplay-grove`
* :ref:`beagleplay-mikrobus`
* :ref:`beagleplay-oldi`
* :ref:`beagleplay-csi`
* :ref:`beagleplay-zephyr-development`
* :ref:`beagleplay-kernel-development`
* :ref:`beagleplay-understanding-boot`
