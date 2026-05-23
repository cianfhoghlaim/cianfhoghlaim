.. _accessories-power-supplies:

Power supplies
###############

Different BeagleBoard products require different power supplies. While BeagleBone Black and other AM335X 
based boards will be fine with a 5V @ 1A, others, such as BeagleBone AI-64 require aleast 5V @ 3A. You 
have to either supply the power via USB jack or a matching (center positive) barrel jack as shown in the table below.

.. note::
    The power supply is not supplied with the board.

.. table:: BeagleBoard power supplies
    
    +----------------------------+-------------------+-------------+-------------------------------------------------------------+
    | Board                      | Connector         | Power       |  Tested accessories                                         |
    +============================+===================+=============+=============================================================+
    | BeagleBone Black           | 2.1mm Barrel Jack | 5V @ 2A     | - `Adafruit <http://www.adafruit.com/products/276>`_        |
    +----------------------------+                   |             | - `Sparkfun <https://www.sparkfun.com/products/8269?>`_     |
    | BeagleBone Black Wireless  |                   |             | - `Logic Supply <http://www.logicsupply.com/pw-5v2a/>`_     |
    +----------------------------+                   |             |                                                             |
    | BeagleV-Ahead              |                   |             |                                                             |
    +----------------------------+                   |             |                                                             |
    | Beaglebone xM              |                   |             |                                                             |
    +----------------------------+-------------------+-------------+-------------------------------------------------------------+
    | PocketBeagle               | microUSB          | 5V @ 2A     | - `AA10A-050A(M)-R <https://mou.sr/3XUPOL0>`_               |
    |                            |                   |             | - `AA10E-050A(M)-R <https://mou.sr/3jrA4zZ>`_               |
    +----------------------------+-------------------+-------------+-------------------------------------------------------------+
    | BeagleBone AI-64           | Type-C            | 5V @ 3A     | - `AA65M-59FKA-R <https://mou.sr/3Dz9P1E>`_                 |
    +----------------------------+                   |             | - `Lenovo 65W USB Type C Adater <https://a.co/d/hH8SbG5>`_  |
    | BeaglePlay                 |                   |             |                                                             |      
    +----------------------------+                   |             |                                                             |
    | BeagleBone AI              |                   |             |                                                             | 
    +----------------------------+                   |             |                                                             |
    | BeagleV-Fire               |                   |             |                                                             |
    +----------------------------+                   |             |                                                             |
    | BeagleY-AI                 |                   |             |                                                             |          
    +----------------------------+-------------------+-------------+-------------------------------------------------------------+
    | BeagleBone Green Gateway   | 2.1mm Barrel Jack | 12V @ 5A    | - `PSAC60M-120-R <https://mou.sr/3Rs657U>`_                 |
    +----------------------------+                   |             |                                                             |
    | Beaglebone Blue            |                   |             |                                                             |
    +----------------------------+-------------------+-------------+-------------------------------------------------------------+
    | BeagleBone X15             | 2.5mm Barrel Jack | 12V @ 5A    | - `TRG70A120-12E01-Level-V <https://mou.sr/3RvRBnl>`_       +
    +----------------------------+-------------------+-------------+-------------------------------------------------------------+

.. tip::
    Most modern day mobile phone chargers are capable of delivering enough current to power any BeagleBone. 
    You may try using that with a suitable cable before buying any standalone power source for your board. Please ensure the expected output voltage
    and current capabilities are listed on your power supply before attempting to power your board. 

If you plan to use capes or add your own circuitry, a power supply capable of higher current may be required.

.. note::
    USB-C supplies will auto-negotiate the highest power mode that both power supply and BeagleBoard support. In most cases, this will be 
    5V @ 3A. It is OK to use a higher Wattage USB-C PD supply with a board, but it is recommended to use supplies from well-known manufacturers to 
    avoid supplies that may break the USB-C PD specification.
