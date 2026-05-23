LED blink using for loop example
================================

.. image:: images/led_pocket_beagle.png
   :width: 598
   :align: center
   :height: 400
   :alt: LED blink using hardware counter
       
Code
----

.. code:: python

   for : l in 0:10 {
       digital_write(P1_31, true);
       delay(1000);
       digital_write(P1_31, false);
       delay(1000);
   }

-  Following code works on PocketBeagle, to use on other boards, please
   change the pins accordingly.

Explanation
------------

This code runs for loop with 10 iterations, Inside ``for`` it sets
header pin P1_31 to HIGH, waits for 1000ms, then sets header pin P1_31
to LOW, then again it waits for 1000ms. This loop runs endlessly, so we
get a Blinking output if one connects a LED. So LED will blink 10 times
with this code.

