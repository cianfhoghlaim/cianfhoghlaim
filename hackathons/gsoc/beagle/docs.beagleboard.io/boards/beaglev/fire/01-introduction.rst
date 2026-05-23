.. _beaglev-fire-introduction:

Introduction
#############

BeagleV®-Fire is a revolutionary SBC powered by the Microchip's PolarFire® MPFS025T System on Chip (SoC) with 4x RV64GC Application cores, 
1x RV64IMAC monitor/boot core, and FPGA fabric. BeagleV®-Fire opens up new horizons for developers, tinkerers, and the open-source community to explore the vast potential 
of RISC-V architecture and FPGA technology. It has the same P8 & P9 cape header pins as BeagleBone Black allowing you to stack your favourite BeagleBone 
cape on top to expand it's capability. Built around the powerful and energy-efficient RISC-V instruction set architecture (ISA) along with its versatile FPGA fabric, 
BeagleV®-Fire SBC offers unparalleled opportunities for developers, hobbyists, and researchers to explore and experiment with RISC-V technology.

.. table::
   :align: center
   :widths: auto

   +----------------------------------------------------+---------------------------------------------------------+
   | .. image:: images/product-pictures/bvf-front.*     | .. image:: images/product-pictures/bvf-back.*           |
   |    :width: 700                                     |       :width: 700                                       |
   |    :align: center                                  |       :align: center                                    |
   |    :alt: BeagleV-Fire front                        |       :alt: BeagleV-Fire back                           |
   +----------------------------------------------------+---------------------------------------------------------+

Pinout Diagrams
***************

Choose the cape header to see respective pinout diagram.

.. tab-set::

   .. tab-item:: P8 cape header

        .. figure:: images/pinout/BeagleV-Fire-P8.*
            :align: center
            :alt: BeagleV-Fire P8 cape header pinout

            BeagleV-Fire P8 cape header pinout


   .. tab-item:: P9 cape header

        .. figure:: images/pinout/BeagleV-Fire-P9.*
            :align: center
            :alt: BeagleV-Fire P9 cape header pinout

            BeagleV-Fire P9 cape header pinout


.. _beaglev-fire-detailed-overview:

Detailed overview
******************

.. table:: BeagleV-Fire features
        
    +----------------------------+---------------------------------------------------------------------------+
    | Feature                    | Description                                                               |
    +============================+===========================================================================+
    | Processor                  | MPFS025T-FCVG484E                                                         |
    +----------------------------+---------------------------------------------------------------------------+
    | Memory                     | 2GB (1Gb x 16)- 1866MHz 3733Mbps, LPDDR4                                  |
    +----------------------------+---------------------------------------------------------------------------+
    | Storage                    | Kingston 16GB eMMC                                                        |
    +----------------------------+---------------------------------------------------------------------------+
    | Wireless                   | 1x M.2 Key E, support 2.4GHz/5GHz WiFi module                             |
    +----------------------------+---------------------------------------------------------------------------+
    | Ethernet                   | - PHY: Realtek RTL8211F-VD-CG Gigabit Ethernet phy                        |
    |                            | - Connector: integrated magnetics RJ-45                                   |
    +----------------------------+---------------------------------------------------------------------------+
    | USB C                      | - Connectivity: Flash/programming support                                 |
    |                            | - Power: Input: 5V @ 3A                                                   |
    +----------------------------+---------------------------------------------------------------------------+
    | Other connectors           | - 1x SYZYGY High speed connector                                          |
    |                            | - microSD card slot                                                       |
    |                            | - CSI connector compatible with BeagleBone AI-64, BeagleV-Ahead, Raspberry|
    |                            |   Pi Zero / CM4 (22-pin)                                                  |
    +----------------------------+---------------------------------------------------------------------------+

Board components location
**************************

This section describes the key components on the board, their location and function.

Front components location
==========================

.. figure:: images/BeagleV-Fire-Front-Annotated.*
    :width: 1400
    :align: center
    :alt: BeagleV-Fire board front components location
    
    BeagleV-Fire board front components location


.. table:: BeagleV-Fire board front components location
    :align: center
        
    +----------------------------+---------------------------------------------------------------------------+
    | Feature                    | Description                                                               |
    +============================+===========================================================================+
    | Power LED                  | Power (Board ON) indicator                                                |
    +----------------------------+---------------------------------------------------------------------------+
    | JTAG (MPFS025T)            | MPFS025T SoC JTAG debug port                                              |
    +----------------------------+---------------------------------------------------------------------------+
    | RTL8211F                   | Gigabit IEEE 802.11 Ethernet PHY                                          |
    +----------------------------+---------------------------------------------------------------------------+
    | P8 & P9 cape header        | Expansion headers for BeagleBone capes.                                   |
    +----------------------------+---------------------------------------------------------------------------+
    | 2GB RAM                    | 2GB (1Gb x 16)- 1866MHz 3733Mbps, LPDDR4                                  |
    +----------------------------+---------------------------------------------------------------------------+
    | 16GB eMMC                  | Kingston 16GB eMMC Flash storage                                          |
    +----------------------------+---------------------------------------------------------------------------+
    | CSI                        | 22pin MIPI Camera connectors                                              |
    +----------------------------+---------------------------------------------------------------------------+
    | M.2 Key E                  | PCIE M.2 Key E connector                                                  |
    +----------------------------+---------------------------------------------------------------------------+
    | UART debug header          | 6 pin UART debug header                                                   |
    +----------------------------+---------------------------------------------------------------------------+
    | Reset button               | Press to reset BeagleV-Fire board (MPFS025T SoC)                          |
    +----------------------------+---------------------------------------------------------------------------+
    | User button                | User defined (custom) action button                                       |
    +----------------------------+---------------------------------------------------------------------------+
    | User LEDs                  | 12x user programmabkle LEDs to show various board status during boot.     |
    +----------------------------+---------------------------------------------------------------------------+
    | GigaBit Ethernet           | 1Gb/s Wired internet connectivity                                         |
    +----------------------------+---------------------------------------------------------------------------+
    | Barrel jack                | Power input                                                               |
    +----------------------------+---------------------------------------------------------------------------+
    | USB C                      | Power, connectivity, and board flashing.                                  |
    +----------------------------+---------------------------------------------------------------------------+

Back components location
=========================

.. figure:: images/BeagleV-Fire-Back-Annotated.*
    :width: 1400
    :align: center
    :alt: BeagleV-Fire board back components location

    BeagleV-Fire board back components location


.. table:: BeagleV-Fire board back components location
    :align: center
        
    +----------------------------+---------------------------------------------------------------------------+
    | Feature                    | Description                                                               |
    +============================+===========================================================================+
    | microSD                    | microSD card slot                                                         |
    +----------------------------+---------------------------------------------------------------------------+
    | SYZYGY                     | SYZYGY High speed connector                                               |
    +----------------------------+---------------------------------------------------------------------------+
    
