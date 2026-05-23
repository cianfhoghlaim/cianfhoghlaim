.. _accessories-cables:

Cables
#######

.. _accessories-cables-usb:

USB Data/Power Cables
***********************

For all Beagles, there is a USB client, also called gadget, capable connection that will enable you to
create network, serial and data storage connections from a host computer.

In most cases, you can also provide power over this same cable.

In most cases, you can also use the port in a host mode, also sometimes called on-the-go to refer
to when a device that is typically a client can also act as a host.

Cable included?
===============

A USB (High-speed A to Mini-B) cable will normally be supplied with BeagleBone Black. For other boards,
you'll have to procure your own USB cable.

What cable is needed?
=====================

The type of cable you have to procure is listed in the table below:

.. table:: USB client capable data/power ports on Beagles

    +----------------------------+---------------------------+---------------+---------------------+
    | Board                      | USB                       | Host capable? | Power required [2]_ |
    +============================+===========================+===============+=====================+
    | BeagleY-AI                 | High-speed USB-C          | Unsupported   | 1000mA              |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeaglePlay                 | High-speed USB-C          | Yes [1]_      | 500mA               |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeagleV-Fire               | High-speed USB-C          | Yes [1]_      | 750mA               |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeagleV-Ahead              | Super-speed Micro-AB      | Yes           | 900mA               |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeagleBone AI-64           | Super-speed USB-C         | Yes [1]_      | 3000mA              |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeagleBone AI              | Super-speed USB-C         | Yes [1]_      | 900mA               |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeagleBone Black           | High-speed Mini-AB        | Yes           | 500mA               |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeagleBone Blue            | High-speed Micro-AB       | Yes           | 500mA               |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeagleBone Black Wireless  | High-speed Micro-AB       | Yes           | 500mA               |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeagleBone (original)      | High-speed Mini-B         | No            | 500mA               |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeagleBoard-xM             | High-speed Micro-AB       | Yes           | 500mA               |
    +----------------------------+---------------------------+---------------+---------------------+
    | BeagleBoard-X15            | High-speed Micro-B        | No            | N/A                 |
    +----------------------------+---------------------------+---------------+---------------------+
    | PocketBeagle               | High-speed Micro-AB       | Yes           | 500mA               |
    +----------------------------+---------------------------+---------------+---------------------+

.. [1] Requires USB client device that does not require specification dictated type-C PD handshake.

.. [2] Power requirement is for the base board in typical operation. Peripherals will add to the power requirement.

.. important::

   BeagleBoard-X15 cannot be powered over the USB port.

.. _serial-debug-cables:

Serial Debug Cables
********************

The default serial port settings for Beagles are:

.. table:: UART settings

    +--------------+--------------+
    | Setting      | Value        |
    +==============+==============+
    | Baud         | 115,200      |
    +--------------+--------------+
    | Bits         | 8            |
    +--------------+--------------+
    | Parity       | N            |
    +--------------+--------------+
    | Stop Bits    | 1            |
    +--------------+--------------+
    | Handshake    | None         |
    +--------------+--------------+

.. _molex-picoblade-serial-cables:

Molex picoblade serial cables
=============================

These cables are not active (only wires and connector) and provide an interface 
between USB to Serial converter cables such as the ones listed below and serial 
debug ports on Beagles such as BeagleBone AI and AI-64. You can purchase these 
cables from different sources including:

1. `Farnell <https://www.newark.com/element14/1103004000156/serial-cable-ai-board/dp/50AH3702>`_
2. `DigiKey <https://www.digikey.com/en/products/detail/digi-key-electronics/BBCAI/10187731>`_

.. note:: 
    BeagleBone AI and BeagleBone AI-64 UART debug port uses a 3pin **Molex PicoBlade (1.25mm)** connector. 
    Raspberry Pi UART debug port uses a 3pin **JST-Sh (1.00mm)** connector. The connectors and the cables 
    for both the connector types may look very similar but they are very different. Make sure to check connector 
    type before buying cables because they are incompatible with each other.

Standard FTDI Cable
====================

The debug cable is a standard FTDI to TTL cable. **Make sure you get the 3.3V version**! 
It can purchased from several different sources including but not limited to:

- `FTDI serial cable direct <https://www.ftdichip.com/Products/Cables/USBTTLSerial.htm>`_
- `FTDI serial cable at DigiKey <https://www.digikey.com/product-detail/en/TTL-232R-3V3/768-1015-ND/1836393>`_
- `FTDI serial cable at Newark <https://www.newark.com/ftdi/ttl-232r-3v3/usb-to-serial-converter-cable/dp/34M8872?st=TTL-232R-3V3>`_
- `FTDI serial cable at Sparkfun <https://www.sparkfun.com/products/9717>`_
- `FTDI serial cable at Adafruit <https://www.adafruit.com/products/70>`_

Other options with different USB to Serial ICs exist and will work as well, such as CP2102, CH340G 
etc but may require additional drivers depending on your operating system.

.. image:: images/FTDI_Cable.jpg
    :align: center
    :alt: FTDI Cable

Pin 1 on the cable is the black wire and connects to pin 1 on the board. (the pin with the white dot next to it)

Adafruit 4 Pin Cable (CP2102)
==============================

`Adafruit 4-pin serial cable <http://www.adafruit.com/products/954>`_ (SiLabs CP2102 based, boards older than 2017 use a Prolific chipset instead)

.. image:: images/RPI_Serial.png
    :align: center
    :alt: 4 pin serial cable
    
.. table:: Adafruit 4 pin serial cable connection to BeagleBone Black

    +--------------+--------------+
    | Board        | Wire         |
    +==============+==============+
    | Pin 1 (GND)  | Black (GND)  |
    +--------------+--------------+
    | Pin 4 (RX)   | Green (TX)   |
    +--------------+--------------+
    | Pin 5 (TX)   | White (RX)   |
    +--------------+--------------+

.. note:: 
    The naming of the signals reflect those of the cable. 
    The swapping of TX and RX takes place on the board.

    You will also find an extra RED wire on this cable 
    that supplies 5V @ 500mA which could power the 
    board if connected to one of the VDD_5V pins. 
    It's recommended that you leave it unconnected.


JTAG debug Cables
*****************

TagConnect (JTAG)
==================

Boards like :ref:`beagleconnect-freedom-home`, :ref:`beaglev-ahead-home`, :ref:`beaglev-fire-home`, and :ref:`beagleplay-home` use the TagConnect 
interface which allows you to perform firmware updates and JTAG hardware debugging. To use the interface, the the parts below from 
`tag-connect <https://www.tag-connect.com>`_  are required.

.. note:: 
    You need both the cable and the retaining clip to properly use/connect the cable with the boards. 
    There is an option to 3D print protective cap and retaining cap which you can try.

TC2050 debug cable
-------------------

.. image:: images/tc2050-idc-nl-10-pin-debug-cable.jpg
    :align: center
    :width: 420
    :alt: TC2050 10pin debug cable
 
1. `TC2050 cable (tag-connect.com) <https://www.tag-connect.com/product/tc2050-idc-nl-10-pin-no-legs-cable-with-ribbon-connector>`_
2. `TC2050 cable (DigiKey) <https://www.digikey.com/en/products/detail/tag-connect-llc/TC2050-IDC-NL/2605367>`_



TC2050 retaining clip
----------------------

.. image:: images/TC2050-CLIP.jpg
    :align: center
    :width: 420
    :alt: TC2050 retaining clip

1. `TC2050 retaining clip (tag-connect.com) <https://www.tag-connect.com/product/tc2050-clip-3pack-retaining-clip>`_
2. `TC2050 retaining clip (DigiKey) <https://www.digikey.com/en/products/detail/tag-connect-llc/TC2050-CLIP-3PACK/12318009>`_

3D printable cap & clip (Optional)
-----------------------------------

.. image:: images/TC2050-protective-cap.jpg
    :align: center
    :width: 420
    :alt: 3D printable TC2050 protective cap


1. `Protective cap (Thingiverse) <https://www.thingiverse.com/thing:3025584>`_
2. `Retaining clip (Thingiverse) <https://www.thingiverse.com/thing:3035278>`_


HDMI Cables
************

Working HDMI Cables
====================

The BeagleBone Black uses a microHDMI cable. 

.. image:: images/MicroHDMI.jpg
    :align: center
    :alt: MicroHDMI to HDMI cable

microHDMI to VGA
=================

`Cable Matters Micro HDMI to VGA Adapter <https://www.amazon.com/Cable-Matters-Active-Female-Adapter/dp/B00879EZJI/ref=sr_1_2?ie=UTF8&qid=1381610066&sr=8-2&keywords=micro-hdmi+to+vga>`_

.. _accessories-cables_minidp_hdmi:

miniDP to HDMI 
****************

Working miniDP to HDMI Adapters
================================

.. note::
    BeagleBone-AI64 requires an **ACTIVE** Mini DisplayPort to HDMI cable or adaptor to work, 
    a passive miniDP to HDMI setup will not work at all.

- `IVANKY 4K Active Mini DisplayPort to HDMI Adapter <https://www.amazon.com/dp/B089GF8M87/>`_
- `CableCreation Mini DP (Thunderbolt 2 Compatible) to HDMI <https://www.amazon.in/CD0257-Mini-DP-to-HDMI/dp/B01FM51O0W/>`_

Examples of "Bad" MiniDP to HDMI Adapters
===========================================

- `UGREEN Mini DP Male to HDMI <https://www.amazon.in/Mini-Male-Female-Converter-Cable/dp/B01CL1P6TA/>`_
- `AGARO Mini Displayport (Mini Dp) To Hdmi <https://www.amazon.in/AGARO-Meters-Laptop-Computers-Mobile/dp/B09GW1NMNZ/>`_
- `AmazonBasics Mini Display Port to HDMI <https://www.amazon.in/AmazonBasics-Mini-DisplayPort-HDMI-Adapter/dp/B0134V3KIA/>`_
