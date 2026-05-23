Digital write example
=====================

.. image:: images/led_pocket_beagle.png
   :width: 598
   :align: center
   :height: 400
   :alt: Digital write example

Code
----

.. code:: python

   while : true {
       digital_write(P1_31, true);
   }

-  Following code works on PocketBeagle, to use on other boards, please
   change the pins accordingly.

Explanation
------------

This code runs a never ending loop, since it is ``while : true``. Inside
``while`` it sets header pin P1_31 to HIGH.

