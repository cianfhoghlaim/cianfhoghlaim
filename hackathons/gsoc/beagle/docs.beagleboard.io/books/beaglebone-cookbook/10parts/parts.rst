.. _beaglebone-cookbook-parts:

.. |I2C| replace:: I\ :sup:`2`\ C
.. |kohm| replace:: kΩ
.. |ohm| replace:: Ω

Parts and Suppliers
####################

The following tables list where you can find the parts used in this book. 
We have listed only one or two sources here, but you can often find a given part in many places.

.. table:: United States suppliers

    +-------------+------------------------------------------------------------------+------------------------------------+
    | Supplier    | Website                                                          | Notes                              |
    +=============+==================================================================+====================================+
    | Adafruit    | http://www.adafruit.com                                          | Good for modules and parts         |
    +-------------+------------------------------------------------------------------+------------------------------------+
    | Amazon      | http://www.amazon.com/                                           | Carries everything                 |
    +-------------+------------------------------------------------------------------+------------------------------------+
    | Digikey     | http://www.digikey.com/                                          | Wide range of components           |
    +-------------+------------------------------------------------------------------+------------------------------------+
    | MakerShed   | http://www.makershed.com/                                        | Good for modules, kits, and tools  |
    +-------------+------------------------------------------------------------------+------------------------------------+
    | SeeedStudio | https://www.seeedstudio.com/SBC-Beaglebone-Original-c-2031.html? | Low-cost modules                   |
    +-------------+------------------------------------------------------------------+------------------------------------+
    | SparkFun    | http://www.sparkfun.com                                          | Good for modules and parts         |
    +-------------+------------------------------------------------------------------+------------------------------------+

.. table:: Other suppliers

    +-----------+----------------------------------+-------------------------------------------------------------------------------------------+
    | Supplier  | Website                          | Notes                                                                                     |
    +===========+==================================+===========================================================================================+
    | Element14 | http://element14.com/BeagleBone  | World-wide BeagleBoard.org-compliant clone of BeagleBone Black, carries many accessories  |
    +-----------+----------------------------------+-------------------------------------------------------------------------------------------+

Prototyping Equipment
======================

Many of the hardware projects in this book use jumper wires and a breadboard. 
We prefer the preformed wires that lie flat on the board. :ref:`parts_jumper` lists places 
with jumper wires, and :ref:`parts_breadboard` shows where you can get breadboards.

.. _parts_jumper:

.. table:: Jumper wires

    +-------------+--------------------------------------------------------------------------------------------+
    | Supplier    | Website                                                                                    |
    +=============+============================================================================================+
    | Amazon      | http://www.amazon.com/Elenco-Piece-Pre-formed-Jumper-Wire/dp/B0002H7AIG                    |
    +-------------+--------------------------------------------------------------------------------------------+
    | Digikey     | http://www.digikey.com/product-detail/en/TW-E012-000/438-1049-ND/643115                    |
    +-------------+--------------------------------------------------------------------------------------------+
    | SparkFun    | https://www.sparkfun.com/products/124                                                      |
    +-------------+--------------------------------------------------------------------------------------------+


.. _parts_breadboard:

.. table:: Breadboards

    +-------------+---------------------------------------------------------------------------------------------------------------------------------------------+
    | Supplier    | Website                                                                                                                                     |
    +=============+=============================================================================================================================================+
    | Amazon      | http://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Dtoys-and-games&field-keywords=breadboards&sprefix=breadboards%2Ctoys-and-games  |
    +-------------+---------------------------------------------------------------------------------------------------------------------------------------------+
    | Digikey     | https://www.digikey.com/en/products/filter/solderless-breadboards/638                                                                       |
    +-------------+---------------------------------------------------------------------------------------------------------------------------------------------+
    | SparkFun    | https://www.sparkfun.com/search/results?term=breadboard                                                                                     |
    +-------------+---------------------------------------------------------------------------------------------------------------------------------------------+
    | CircuitCo   | https://elinux.org/BeagleBoneBreadboard (no longer manufactured, but design available)                                                      |
    +-------------+---------------------------------------------------------------------------------------------------------------------------------------------+

If you want something more permanent, try `Adafruit's Perma-Proto Breadboard <https://www.adafruit.com/product/1609>`_, 
laid out like a breadboard.

.. _app_resistor:

Resistors
==========

We use 220 , 1k, 4.7k, 10k, 20k, and 22 |kohm| resistors in this book. 
All are 0.25 W.  The easiest way to get all these, and many more, is to order 
`SparkFun's Resistor Kit <http://bit.ly/1EXREh8>`_.  
It's a great way to be ready for future projects, because it has 500 resistors. 

If you don't need an entire kit of resistors, you can order a la carte from a number of places. 
DigiKey has more than a quarter million 
`through-hole resistors <http://bit.ly/1C6WQjZ>`_ at good prices, but make sure you are ordering the right one.

You can find the 10 |kohm| trimpot (or variable resistor) at `SparkFun 10k POT <http://bit.ly/18ACvpm>`_ or 
`Adafruit 10k POT <http://bit.ly/1NKg1Tv>`_.

Flex resistors (sometimes called *flex sensors* or *bend sensors*) are available at 
`SparkFun flex resistors <http://bit.ly/1Br7HD2>`_ and `Adafruit flex resistors <http://bit.ly/1HCGoql>`_.

Transistors and Diodes
=======================

The `2N3904 <http://bit.ly/1B4J8H4>`_ is a common NPN transistor that you can get almost anywhere. 
Even `Amazon NPN transitor <http://amzn.to/1AjvcsD>`_ has it. `Adafruit NPN transitor <http://bit.ly/1b2dgxT>`_ has a nice 10-pack. 
`SparkFun NPN transitor <http://bit.ly/1GrZj5P>`_ lets you buy them one at a time.  `DigiKey NPN transitor <http://bit.ly/1GF8H9K>`_
will gladly sell you 100,000.

The `1N4001 <http://bit.ly/1EbRzF6>`_ is a popular 1A diode. Buy one at `SparkFun diode <http://bit.ly/1Ajw54G>`_, 
10 at `Adafruit diode <http://bit.ly/1Gs05zP>`_, 
or 10,000 at `DigiKey diode <https://www.digikey.com/en/products/detail/mdd/1N4001/15517721>`_.

Integrated Circuits
=====================

The PCA9306 is a small integrated circuit (IC) that converts voltage levels between 3.3 V and 5 V. You can get it 
cheaply in large quantities from `DigiKey PCA9306 <http://bit.ly/1Fb8REd>`_, but it's in a very small, hard-to-use, surface-mount 
package. Instead, you can get it from `SparkFun PCA9306 on a Breakout board <http://bit.ly/19ceTsd>`_, which plugs into a breadboard.

The L293D is an `H-bridge IC <http://bit.ly/1wujQqk>`_ with which you can control large loads (such as motors) in 
both directions.  `SparkFun L293D <http://bit.ly/18bXChR>`_, `Adafruit L293D <http://bit.ly/1xd43Yh>`_, and 
`DigiKey L293D <https://www.digikey.com/en/products/detail/stmicroelectronics/L293D/634700>`_ 
all have it in a DIP package that easily plugs into a breadboard.

The ULN2003 is a 7 darlington NPN transistor IC array used to drive motors one way. You can get it from  
`DigiKey ULN2003 <https://www.digikey.com/en/products/detail/texas-instruments/ULN2003AN/277624>`_. 
A possible substitution is ULN2803 available from 
`SparkFun ULN2003 <http://bit.ly/1xd4oKy>`_ and `Adafruit ULN2003 <http://bit.ly/1EXWhaU>`_.

The TMP102 is an |I2C|-based digital temperature sensor. You can buy them in bulk from 
`DigiKey TMP102 <https://www.digikey.com/en/products/filter/temperature-sensors/analog-and-digital-output/518?s=N4IgTCBcDaIC4FsAOBGADBAugXyA>`_, 
but it's too small for a breadboard. `SparkFun TMP102 <http://bit.ly/1GFafAE>`_
sells it on a breakout board that works well with a breadboard.

The DS18B20 is a one-wire digital temperature sensor that looks like a three-terminal transistor. 
Both `SparkFun DS18B20 <http://bit.ly/1Fba7Hv>`_ and `Adafruit DS18B20 <http://bit.ly/1EbSYvC>`_ carry it.


Opto-Electronics
=================

`LEDs <http://bit.ly/1BwZvQj>`_ are *light-emitting diodes*. LEDs come in a wide range of colors, 
brightnesses, and styles. You can get a basic red LED at `SparkFun red LED <http://bit.ly/1GFaHPi>`_, 
`Adafuit red LED <http://bit.ly/1GFaH1M>`_, and `DigiKey red LED <http://bit.ly/1b2f2PD>`_.

Many places carry bicolor LED matrices, but be sure to get one with an |I2C| interface. 
`Adafruit LED matrix <http://bit.ly/18AENVn>`_ is where I got mine.

Capes
======

There are a number of sources for capes for BeagleBone Black. 
`BeagleBoard.org capes page <http://docs.beagleboard.org/>`_ keeps a current list.

Miscellaneous
==============

Here are some things that don't fit in the other categories.

.. table:: Miscellaneous

    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | 3.3 V FTDI cable                                    | `SparkFun FTDI cable <http://bit.ly/1FMeXsG>`_,                                       |
    |                                                     | `Adafruit FTDI cable <http://bit.ly/18AF1Mm>`_                                        |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | USB WiFi adapter                                    | `Adafruit WiFi adapter <http://www.adafruit.com/products/814>`_                       |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | HDMI cable                                          | `SparkFun HDMI cable <https://www.sparkfun.com/products/11572>`_                      |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Micro HDMI to HDMI cable                            | `Adafruit HDMI to microHDMI cable <http://www.adafruit.com/products/1322>`_           |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | HDMI to DVI Cable                                   | `SparkFun HDMI to DVI cable <https://www.sparkfun.com/products/12612>`_               |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | HDMI monitor                                        | `Amazon HDMI monitor <http://amzn.to/1B4MABD>`_                                       |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Powered USB hub                                     | `Amazon power USB hub <http://amzn.to/1NKm2zB>`_,                                     |
    |                                                     | `Adafruit power USB hub <http://www.adafruit.com/products/961>`_                      |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Soldering iron                                      | `SparkFun soldering iron <http://bit.ly/1FMfUkP>`_,                                   |
    |                                                     | `Adafruit soldering iron <http://bit.ly/1EXZ6J1>`_                                    |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Oscilloscope                                        | `Adafruit oscilloscope <https://www.adafruit.com/products/468>`_                      |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Multimeter                                          | `SparkFun multimeter <http://bit.ly/1C5BUbu>`_,                                       |
    |                                                     | `Adafruit multimeter <http://bit.ly/1wXX3np>`_                                        |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | PowerSwitch Tail II                                 | `SparkFun PowerSwitch Tail II <http://bit.ly/1Ag5bLP>`_,                              | 
    |                                                     | `Adafruit PowerSwitch Tail II <http://bit.ly/1wXX8aF>`_                               |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Servo motor                                         | `SparkFun servo motor <http://bit.ly/1C72cvw>`_,                                      |
    |                                                     | `Adafruit servo motor <http://bit.ly/1HCPQdl>`_                                       |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | 5 V power supply                                    | `SparkFun 5V power supply <http://bit.ly/1C72q5C>`_,                                  |
    |                                                     | `Adafruit 5V power supply <http://bit.ly/18c0n2D>`_                                   |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | 3 V to 5 V motor                                    | `SparkFun 3V-5V motor <http://bit.ly/1b2g65Y>`_,                                      |
    |                                                     | `Adafruit 3V-5V motor <http://bit.ly/1C72DWF>`_                                       |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | 3 V to 5 V bipolar stepper motor                    | `SparkFun 3V-5V bipolar stepper motor <http://bit.ly/1Bx2hVU>`_,                      |
    |                                                     | `Adafruit 3V-5V bipolar stepper motor <http://bit.ly/18c0HhV>`_                       |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | 3 V to 5 V unipolar stepper motor                   | `Adafruit 3V-5V unipolar stepper motor <http://www.adafruit.com/products/858>`_       |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Pushbutton switch                                   | `SparkFun pushbutton switch <http://bit.ly/1AjDf90>`_,                                |
    |                                                     | `Adafruit pushbutton switch <http://bit.ly/1b2glhw>`_                                 |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Magnetic reed switch                                | `SparkFun magnetic reed switch <https://www.sparkfun.com/products/8642>`_             |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | LV-MaxSonar-EZ1 Sonar Range Finder                  | `SparkFun LV-MaxSonar-EZ1 <http://bit.ly/1C73dDH>`_,                                  |
    |                                                     | `Amazon LV-MaxSonar-EZ1 <http://amzn.to/1wXXvlP>`_                                    |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | HC-SR04 Ultrsonic Range Sensor                      | `Amazon HC-SR04 <http://amzn.to/1FbcPNa>`_                                            |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Rotary encoder                                      | `SparkFun rotary encoder <http://bit.ly/1D5ZypK>`_,                                   |
    |                                                     | `Adafruit rotary encoder <http://bit.ly/1D5ZGp3>`_                                    |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | GPS receiver                                        | `SparkFun GPS <http://bit.ly/1EA2sn0>`_,                                              |
    |                                                     | `Adafruit GPS <http://bit.ly/1MrS2VV>`_                                               |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | BLE USB dongle                                      | `Adafruit BLE USB dongle <http://www.adafruit.com/products/1327>`_                    |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Syba SD-CM-UAUD USB Stereo Audio Adapter            | `Amazon USB audio adapter <http://amzn.to/1EA2GdI>`_                                  |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Sabrent External Sound Box USB-SBCV                 | `Amazon USB audio adapter (alt) <http://amzn.to/1C74kTU>`_                            |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
    | Vantec USB External 7.1 Channel Audio Adapter       | `Amazon USB audio adapter (alt2) <http://amzn.to/19cinev>`_                           |
    +-----------------------------------------------------+---------------------------------------------------------------------------------------+
