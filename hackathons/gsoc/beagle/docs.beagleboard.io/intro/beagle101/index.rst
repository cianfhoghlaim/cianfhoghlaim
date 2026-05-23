.. _intro_beagle-101:

An Introduction to Beagles
##########################

The most common path to using a Beagle is to use a body of open source software. The
primary open source targets supported by the BeagleBoard.org community are:

* :ref:`intro-beagle-linux` and
* :ref:`intro-beagle-zephyr`.

Many other paths are possible, but, if you don't already have a path, these are the
ones to typically go down.

If you are new to embedded systems in general, you might consider starting at:

* :ref:`intro-embedded-systems`

.. toctree::
   :maxdepth: 1
   :hidden:

   blinkLED
   c
   assembly
   verilog
   basic-wiring
   embedded-serial
   qwiic-stemma-grove-addons
   motors
   zephyr
   linux
   device-tree
   fpga
   verification
   arm
   riscv
   openbeagle-ci
   buildroot
   debian
   wireless-communications

.. _intro-beagle-linux:

Getting started with Linux
**************************

Most Beagles have on-board flash preconfigured to run Linux. These resources will get you started quickly.

Linux Basics
============

* Get started at :ref:`blinkLED`.
* Learn to reset a board back to factory defaults and dive a bit deeper into the IDE at :ref:`beagleboard-getting-started`.
* Learn a bit about Linux at :ref:`intro-linux`.
* Learn about accessories at :ref:`accessories-home`
* Learn about using 3rd party I2C add-on boards at :ref:`qwiic_stemma_grove_addons`.
* Learn about using mikroBUS add-on boards at :ref:`beagleplay-mikrobus`.
* Learn about using Cape add-on boards at :ref:`capes`.
* Learn about device tree at :ref:`intro-device-tree`.
* Read :ref:`bone-cook-book-home`.
* Read :ref:`pru-cookbook-home`.
* Find more books at https://www.beagleboard.org/books.

More on Linux
=============

* :ref:`intro-buildroot`
* :ref:`intro-debian`

.. _intro-beagle-zephyr:

Getting started with Zephyr
***************************

Our Zephyr-enabled boards ship with a build of Micropython and, in the future, will also
ship with a BeagleConnect Greybus node service for quick, transparent access from any BeagleConnect
Greybus host enabled system.

Zephyr Basics
=============

* Learn a bit about Zephyr at :ref:`intro-zephyr`
* See :ref:`beagleconnect-freedom-using-micropython` to get started quickly.
* See :ref:`beagleconnect-freedom-using-zephyr` to learn to setup the Zephyr SDK.
* See :ref:`beagleconnect-overview` to learn about BeagleConnect Greybus.

.. _intro-embedded-systems:

Getting started with embedded systems
*************************************

An embedded system is a computer designed not to look like a computer. That is, it
is designed to work like an applicance, doing what you need when you need it, rather
than sitting around trying to get your attention and begging to be told what to do.

An embedded system is built around a computer, but adds additional sensors and
actuators to do a task, like make toast or get you to work on time along using the
freeway. We don't typically call these things computers. Instead, we call them "toasters"
or "cars". At the heart of these machines is often a programmable computer, though it
might not be programmable by *you*.

At BeagleBoard.org, we seek to enable you to make embedded systems of your own, rather
than relying on other people to make them for you. You could call it DIY, or do-it-yourself,
but the reality is more DIT, or do-it-together. The skills and tools to build an embedded
system are very complicated and the fundamental manufacturing tools are very expensive, so we
need to work together to build even the simplest of embedded systems.

Of course, there is nothing wrong with building a dumb toaster, it might even be preferred.
However, if you are building a smart toaster, you might want it to obey you, rather than
someone 50,000 km away.

Embedded Systems Basics
=======================

Here are some basic skills to building an embedded system:

* :ref:`intro-c`
* :ref:`intro-assembly`
* :ref:`intro-verilog`

More on Embedded Systems
========================

Here are some more advanced topics around building an embedded system:

* :ref:`intro-fpga`
* :ref:`intro-verification`
* :ref:`intro-arm`
* :ref:`intro-riscv`
* :ref:`intro-wireless-communications`

.. todo::

   Make sure we have everything critical from https://beagleboard.github.io/bone101/Support/bone101/
