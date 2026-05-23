Delay example
=============

.. image:: images/led_pocket_beagle.png
   :width: 598
   :align: center
   :height: 400
   :alt: Delay example


Code
----

.. code:: python

   digital_write(P1_31, true);
   delay(2000);
   digital_write(P1_31, false);
   delay(5000);
   digital_write(P1_31, true);

-  Following code works on PocketBeagle, to use on other boards, please
   change the pins accordingly.

Explanation
------------

This code snippet writes HIGH to header pin P1_31, then waits for 2000ms
using the ``delay`` call, after that it writes LOW to header pin P1_31,
then again waits for 5000ms using the ``delay`` call, and finally writes
HIGH to header pin P1_31.

