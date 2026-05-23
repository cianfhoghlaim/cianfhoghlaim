.. _simppru_basics:

simpPRU Basics
###############

The PRU is a dual core micro-controller system present on the AM335x SoC
which powers the BeagleBone. It is meant to be used for high speed
jitter free IO control. Being independent from the linux scheduler and
having direct access to the IO pins of the BeagleBone Black, the PRU is
ideal for offloading IO intensive tasks.

Programming the PRU is a uphill task for a beginner, since it involves
several steps, writing the firmware for the PRU, writing a loader
program. This can be a easy task for a experienced developer, but it
keeps many creative developers away. So, I propose to implement a easy
to understand language for the PRU, hiding away all the low level stuff
and providing a clean interface to program PRU.

This can be achieved by implementing a language on top of PRU C. It will
directly compile down to PRU C. This could also be solved by
implementing a bytecode engine on the PRU, but this will result in waste
of already limited resources on PRU. With this approach, both PRU cores
can be run independent of each other.

.. image:: images/simpPRU.png
   :width: 398
   :align: center
   :height: 200
   :alt: simpPRU


What is simpPRU
---------------

-  simpPRU is a procedural programming language.
-  It is a statically typed language. Variables and functions must be
   assigned data types during compilation.
-  It is type-safe, and data types of variables are decided during
   compilation.
-  simpPRU codes have a ``.sim`` extension.
-  simpPRU provides a console app to use Remoteproc functionality.