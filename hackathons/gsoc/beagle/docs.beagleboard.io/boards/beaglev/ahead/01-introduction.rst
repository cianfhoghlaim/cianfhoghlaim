.. _beaglev-ahead-introduction:

Introduction
#############

BeagleV-Ahead is a high-performance open-source RISC-V single board computer (SBC) built around the Alibaba TH1520 SoC. It has the same P8 & P9 cape header pins as
BeagleBone Black allowing you to stack your favourite BeagleBone cape on top to expand it's capability.
Featuring a powerful quad-core RISC-V processor BeagleV Ahead is designed as an affordable
RISC-V enabled pocket-size computer for anybody who want's to dive deep into the new RISC-V ISA.

.. table::
   :align: center
   :widths: auto

   +----------------------------------------------------+---------------------------------------------------------+
   | .. image:: images/product-pictures/front.*         | .. image:: images/product-pictures/back.*               |
   |    :width: 700                                     |       :width: 700                                       |
   |    :align: center                                  |       :align: center                                    |
   |    :alt: BeagleV Ahead front                       |       :alt: BeagleV Ahead back                          |
   +----------------------------------------------------+---------------------------------------------------------+

Pinout Diagrams
***************

Choose the cape header to see respective pinout diagram.

.. tab-set::

   .. tab-item:: P8 cape header

        .. figure:: images/pinout/BeagleV-Ahead-P8.*
            :align: center
            :alt: BeagleV Ahead P8 cape header pinout

            BeagleV Ahead P8 cape header pinout


   .. tab-item:: P9 cape header

        .. figure:: images/pinout/BeagleV-Ahead-P9.*
            :align: center
            :alt: BeagleV Ahead P9 cape header pinout

            BeagleV Ahead P9 cape header pinout

.. _beaglev-ahead-detaild-overview:

Detailed overview
******************

BeagleV Ahead is build around T-Head TH1520 RISC-V SoC with quad-core 
Xuantie C910 processor clocked at 1.85GHz with a 4 TOPS NPU, support for 
64-bit DDR, and audio processing using a single core C906.

.. todo::

    remove "<To-Do>" items in the table below.

.. table:: BeagleV Ahead features
        
    +----------------------------+---------------------------------------------------------------------------+
    | Feature                    | Description                                                               |
    +============================+===========================================================================+
    | Processor                  | T-Head TH1520 (quad-core Xuantie C910 processor)                          |
    +----------------------------+---------------------------------------------------------------------------+
    | PMIC                       | DA9063                                                                    |
    +----------------------------+---------------------------------------------------------------------------+
    | Memory                     | 4GB LPDDR4                                                                |
    +----------------------------+---------------------------------------------------------------------------+
    | Storage                    | 16GB eMMC                                                                 |
    +----------------------------+---------------------------------------------------------------------------+
    | WiFi/Bluetooth             | - PHY: AP6203BM                                                           |
    |                            | - Antennas: 2.4GHz & 5GHz                                                 |
    +----------------------------+---------------------------------------------------------------------------+
    | Ethernet                   | - PHY: Realtek RTL8211F-VD-CG Gigabit Ethernet phy                        |
    |                            | - Connector: integrated magnetics RJ-45                                   |
    +----------------------------+---------------------------------------------------------------------------+
    | microUSB 3.0               | - Connectivity: USB OTG, Flash support                                    |
    |                            | - Power: Input: 5V @ <To-Do>, Output: 5V @ <To-Do>                        |
    +----------------------------+---------------------------------------------------------------------------+
    | HDMI                       | - Transmitter: TH1520 Video out system                                    |
    |                            | - Connector: Mini HDMI                                                    |
    +----------------------------+---------------------------------------------------------------------------+
    | Other connectors           | - microSD                                                                 |
    |                            | - mikroBUS shuttle connector (I2C/UART/SPI/ADC/PWM/GPIO)                  |
    |                            | - 2 x CSI connector compatible with BeagleBone AI-64,                     |
    |                            |   Raspberry Pi Zero / CM4 (22-pin)                                        |
    |                            | - DSI connector                                                           |
    +----------------------------+---------------------------------------------------------------------------+

Board components location
**************************

This section describes the key components on the board, their location and function.

Front components location
==========================

.. figure:: images/components-front.*
    :width: 1400
    :align: center
    :alt: BeagleV Ahead board front components location

    BeagleV Ahead board front components location


.. table:: BeagleV Ahead board front components location
    :align: center
        
    +----------------------------+---------------------------------------------------------------------------+
    | Feature                    | Description                                                               |
    +============================+===========================================================================+
    | Power LED                  | Power (Board ON) indicator                                                |
    +----------------------------+---------------------------------------------------------------------------+
    | JTAG (TH1520)              | TH1520 SoC JTAG debug port                                                |
    +----------------------------+---------------------------------------------------------------------------+
    | Barrel jack                | Power input                                                               |
    +----------------------------+---------------------------------------------------------------------------+
    | GigaBit Ethernet           | 1Gb/s Wired internet connectivity                                         |
    +----------------------------+---------------------------------------------------------------------------+
    | User LEDs                  | Five user LEDs, :ref:`board-power-and-boot` section provides more details.|
    |                            | These LEDs are connect to the TH1520 SoC                                  |
    +----------------------------+---------------------------------------------------------------------------+
    | Reset button               | Press to reset BeagleV Ahead board (TH1520 SoC)                           |
    +----------------------------+---------------------------------------------------------------------------+
    | Power button               | Press to shut-down (OFF), hold down to boot (ON)                          |
    +----------------------------+---------------------------------------------------------------------------+
    | P8 & P9 cape header        | Expansion headers for BeagleBone capes.                                   |
    +----------------------------+---------------------------------------------------------------------------+
    | UART debug header          | 6 pin UART debug header                                                   |
    +----------------------------+---------------------------------------------------------------------------+
    | USB boot button            | Hold and reset board (power cycle) to flash eMMC via USB port             |
    +----------------------------+---------------------------------------------------------------------------+
    | SD boot button             | Hold and reset board (power cycle) to boot from SD Card                   |
    +----------------------------+---------------------------------------------------------------------------+
    | mikroBUS shuttle           | 16pin mikroBUS shuttle connector for interfacing mikroE click boards      |
    +----------------------------+---------------------------------------------------------------------------+
    | 16GB eMMC                  | Flash storage                                                             |
    +----------------------------+---------------------------------------------------------------------------+
    | RTL8211F                   | Gigabit IEEE 802.11 Ethernet PHY                                          |
    +----------------------------+---------------------------------------------------------------------------+


Back components location
=========================

.. figure:: images/components-back.*
    :width: 1400
    :align: center
    :alt: BeagleV Ahead board back components location

    BeagleV Ahead board back components location


.. table:: BeagleV Ahead board back components location
    :align: center
        
    +----------------------------+---------------------------------------------------------------------------+
    | Feature                    | Description                                                               |
    +============================+===========================================================================+
    | DA9063                     | Dialog semi Power Management Integrated Circuit (PMIC)                    |
    +----------------------------+---------------------------------------------------------------------------+
    | microUSB 3.0               | Power & USB connectivity as client or Host (OTG)                          |
    +----------------------------+---------------------------------------------------------------------------+
    | Antenna connector          | 2.4GHz/5GHz uFL connector                                                 |
    +----------------------------+---------------------------------------------------------------------------+
    | AP6203BM                   | Ampak WiFi & BlueTooth combo                                              |
    +----------------------------+---------------------------------------------------------------------------+
    | DSI                        | MIPI Display connector                                                    |
    +----------------------------+---------------------------------------------------------------------------+
    | CSI0 & CSI1                | MIPI Camera connectors                                                    |
    +----------------------------+---------------------------------------------------------------------------+
    | TH1520                     | T-Head quad-core C910 RISC-V SoC                                          |
    +----------------------------+---------------------------------------------------------------------------+
    | Mini HDMI                  | HDMI connector                                                            |
    +----------------------------+---------------------------------------------------------------------------+
    | microSD                    | Micro SD card holder                                                      |
    +----------------------------+---------------------------------------------------------------------------+
    | 4GB RAM                    | 2 x 2GB LPDDR4 RAM                                                        |
    +----------------------------+---------------------------------------------------------------------------+

