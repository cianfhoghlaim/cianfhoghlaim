.. _beaglev-fire-design:

Design & specifications
#######################

If you want to know how BeagleV-Fire board is designed and what are it's 
high-level specifications then this chapter is for you. We are going to discuss 
each hardware design element in detail and provide high-level device 
specifications in  a short and crisp form as well.

.. tip:: 

    For hardware design files and schematic diagram you can checkout BeagleV-Fire 
    GitLab repository: https://git.beagleboard.org/beaglev-fire/beaglev-fire

Block diagram
**************

.. figure:: images/hardware-design/system-block-diagram.*
    :width: 720
    :align: center
    :alt: System block diagram

    System block diagram

.. figure:: images/hardware-design/power-tree-diagram.*
    :width: 720
    :align: center
    :alt: Power tree diagram

    Power tree diagram

.. figure:: images/hardware-design/iic-tree-diagram.*
    :width: 420
    :align: center
    :alt: I2C tree diagram

    I2C tree diagram
 
System on Chip (SoC)
*********************

.. figure:: images/hardware-design/soc-bank0.*
    :width: 720
    :align: center
    :alt: SoC bank0

    SoC bank0

.. figure:: images/hardware-design/soc-bank1.*
    :width: 720
    :align: center
    :alt: SoC bank1

    SoC bank1

.. figure:: images/hardware-design/soc-bank2.*
    :width: 540
    :align: center
    :alt: SoC bank2

    SoC bank2

.. figure:: images/hardware-design/soc-bank3.*
    :width: 720
    :align: center
    :alt: SoC bank3

    SoC bank3

.. figure:: images/hardware-design/soc-bank4.*
    :width: 420
    :align: center
    :alt: SoC bank4

    SoC bank4

.. figure:: images/hardware-design/soc-power.*
    :width: 970
    :align: center
    :alt: SoC power

    SoC power


Power management
*****************

.. figure:: images/hardware-design/dc-5v-input.*
    :width: 720
    :align: center
    :alt: DC 5V input

    DC 5V input

.. figure:: images/hardware-design/ideal-diode.*
    :width: 420
    :align: center
    :alt: Ideal diode

    Ideal diode

.. figure:: images/hardware-design/vcc-1v0.*
    :width: 720
    :align: center
    :alt: VCC 1V0

    VCC 1V0

.. figure:: images/hardware-design/vcc-1v1.*
    :width: 720
    :align: center
    :alt: VCC 1V1

    VCC 1V1

.. figure:: images/hardware-design/vcc-1v8.*
    :width: 720
    :align: center
    :alt: VCC 1V8

    VCC 1V8

.. figure:: images/hardware-design/vcc-2v5.*
    :width: 270
    :align: center
    :alt: VCC 2V5

    VCC 2V5

.. figure:: images/hardware-design/vcc-3v3.*
    :width: 720
    :align: center
    :alt: VCC 3V3

    VCC 3V3

.. figure:: images/hardware-design/vcca-1v0.*
    :width: 540
    :align: center
    :alt: VCCA 1V0

    VCCA 1V0

.. figure:: images/hardware-design/vio-enable.*
    :width: 720
    :align: center
    :alt: VIO enable

    VIO enable

General Connectivity and Expansion
**********************************

USB-C port
============

.. figure:: images/hardware-design/usb-c.*
    :width: 970
    :align: center
    :alt: USB C

    USB C

P8 & P9 cape header pins
=========================

.. figure:: images/hardware-design/p8-header.*
    :width: 570
    :align: center
    :alt: P8 cape header

    P8 cape header

.. figure:: images/hardware-design/p9-header.*
    :width: 570
    :align: center
    :alt: P9 cape header

    P9 cape header

.. figure:: images/hardware-design/level-translator.*
    :width: 1070
    :align: center
    :alt: Cape header voltage level translator

    Cape header voltage level translator

ADC
===

.. figure:: images/hardware-design/adc.*
    :width: 720
    :align: center
    :alt: 16bit Delta-Sigma ADC

    16bit Delta-Sigma ADC

.. figure:: images/hardware-design/adc-ldo.*
    :width: 270
    :align: center
    :alt: ADC LDO power supply

    ADC LDO power supply

Buttons and LEDs
******************

User LEDs and Power LED
========================

.. figure:: images/hardware-design/leds.*
    :width: 720
    :align: center
    :alt: User LEDs and power LED

    User LEDs and power LED

User and reset button
=======================

.. figure:: images/hardware-design/user-button.*
    :width: 420
    :align: center
    :alt: User button

    User button

.. figure:: images/hardware-design/reset-button.*
    :width: 420
    :align: center
    :alt: Reset button

    Reset button

Connectivity
**************

Ethernet
========

.. figure:: images/hardware-design/gigabit-ethernet.*
    :width: 970
    :align: center
    :alt: Gigabit ethernet

    Gigabit ethernet

Memory, Media and Data storage
********************************

DDR memory
==========

.. figure:: images/hardware-design/lpdd4.*
    :width: 970
    :align: center
    :alt: LPDDR memory

    LPDDR memory

eMMC
=====

.. figure:: images/hardware-design/emmc.*
    :width: 970
    :align: center
    :alt: EMMC flash storage

    EMMC flash storage

microSD
=======

.. figure:: images/hardware-design/sdcard.*
    :width: 970
    :align: center
    :alt: SD Card socket

    SD Card socket

EEPROM
======

.. figure:: images/hardware-design/eeprom.*
    :width: 420
    :align: center
    :alt: EEPROM

    EEPROM

SPI flash
==========

.. figure:: images/hardware-design/spi-flash.*
    :width: 470
    :align: center
    :alt: SPI Flash

    SPI Flash

Multimedia I/O
***************

CSI
====

.. figure:: images/hardware-design/csi.*
    :width: 470
    :align: center
    :alt: CSI

    CSI

Debug
******

UART debug port 
===============

.. figure:: images/hardware-design/uart-debug-header.*
    :width: 470
    :align: center
    :alt: UART debug header

    UART debug header

JTAG debug port
===============

.. figure:: images/hardware-design/jtag.*
    :width: 470
    :align: center
    :alt: JTAG debug header

    JTAG debug header


Mechanical Specifications 
**************************

.. table:: Dimensions & weight

    +--------------------+----------------------------------------------------+
    | Parameter          | Values                                             |
    +====================+====================================================+
    | Size               | 86.38 * 54.61 * 18.8 mm                            |
    +--------------------+----------------------------------------------------+
    | Max heigh          | 18.8 mm                                            |
    +--------------------+----------------------------------------------------+
    | PCB Size           | 86.38 * 54.6 mm                                    |
    +--------------------+----------------------------------------------------+
    | PCB Layers         | 12 Layers                                          |
    +--------------------+----------------------------------------------------+
    | PCB Thickness      | 1.6 mm                                             |
    +--------------------+----------------------------------------------------+
    | RoHS compliant     | Yes                                                |
    +--------------------+----------------------------------------------------+
    | Gross Weight       | 106 g                                              |
    +--------------------+----------------------------------------------------+
    |  Net weight        | 45.8 g                                             |
    +--------------------+----------------------------------------------------+