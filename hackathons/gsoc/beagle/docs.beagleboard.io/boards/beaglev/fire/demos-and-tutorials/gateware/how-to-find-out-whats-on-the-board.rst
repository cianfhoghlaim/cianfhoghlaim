.. _beaglev-fire-gateware-version:

How to retrieve BeagleV-Fire's gateware version
###############################################

There are two methods to find out what gateware is programmed on a board.

Device Tree
===========
The device tree overlays contains the list of gateware blocks included in the overall gateware design.
You can retrieve that information using the following command:

.. code-block::

    tree /proc/device-tree/chosen/overlays/

This should give an output similar to the one below.

.. figure:: images/dts-design-info.png
    :align: center

The gateware version can be retrieve by reading one of the overlay files. For example, the command:

.. code-block::

    cat /proc/device-tree/chosen/overlays/ROBOTICS-CAPE-GATEWARE


should result in:

.. figure:: images/dts-design-version.png
    :align: center

where the result of a "git describe" command on the gateware repository is displayed. This provides the
most recent tag on the gateware repository followed by information about additionanl commits if some
exist. In the example above, the gateware was created from a gateware repository hash 3e0d338 which is
5 commits more recent than tag BVF-0.3.0.

Bootloader messages
===================
The Hart Software Services display the gateware design name and design version retrieve from the FPGA
at system start-up.

.. figure:: images/hss-design-info.png
    :align: center

The design name is the name of the build option selected when using the bitstream-builder to generate
the bitstream. The number at the end of the design name is the hash of the gateware repository used
to build the bitstream.

The design version is specified as part of the bitstream-builder build configuration option.

Please note that design name "BVF_GATEWARE" indicates that the bitstream used to program the board was
generated directly from the gateware repositories scripts and not the bitstream-builder. You might
see this when customizing the gateware. Seeing "BVF_GATEWARE" as the design name should be a warning
sign that there is a disconnect between the hardware and software on your board.
