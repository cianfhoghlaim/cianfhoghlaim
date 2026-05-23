.. _pocketbeagle-2-introduction:

Introduction
###############

PocketBeagle 2 is based on `Texas Instrments AM6232 SoC <https://www.ti.com/product/AM623>`_, it's dual A53 cores can 
provides higher performance than classic PocketBeagle. The new design comes with pre-soldered headers, 
3-pin JST-SH 1.00mm uart debug port, USB-C port, MSPM0L1105, 512MB RAM, and LiPo Battery charger.

.. table::
   :align: center
   :widths: auto

   +----------------------------------------------------+---------------------------------------------------------+
   | .. image:: images/product/pocketbeagle-2-front.*   | .. image:: images/product/pocketbeagle-2-back.*         |
   |    :width: 700                                     |       :width: 700                                       |
   |    :align: center                                  |       :align: center                                    |
   |    :alt: PocketBeagle 2 front                      |       :alt: PocketBeagle 2 back                         |
   +----------------------------------------------------+---------------------------------------------------------+


.. _pocketbeagle-2-comparison:

Comparison
***************

The board is intended to provide functionality well beyond classic PocketBeagle, 
while still providing compatibility with PocketBeagle's expansion headers as 
much as possible. There are several significant differences between the designs. 

.. _pocketbeagle-comparison-table, PocketBeagle comparison:

.. table:: Table: PocketBeagle comparison

   +-------------------+---------------------+----------------------------+
   | Feature           | PocketBeagle 2      | PocketBeagle original      |
   +===================+=====================+============================+
   | SoC               | AM6232              | AM3358                     |
   +-------------------+---------------------+----------------------------+
   | Arm CPU           | Cortex-A53 (64-bit) | Cortex-A8 (32-bit)         |
   +-------------------+---------------------+----------------------------+
   | Arm cores         | 2 x 1GHz            | 1 x 1GHz                   |
   +-------------------+---------------------+----------------------------+
   | RAM               | 512MB DDR4          | 512MB DDR3                 |
   +-------------------+---------------------+----------------------------+


.. todo::

   add cape compatibility details


.. _pocketbeagle-2-features-and-specificationd:

PocketBeagle 2 Features and Specification
********************************************

This section covers the specifications and features of the board and provides a high level 
description of the major components and interfaces that make up the board.

.. _pocketbeagle-2-features,PocketBeagle 2 features tabled:

.. table:: Table: PocketBeagle 2 Features and Specification

   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+
   |                         | Feature                                                                                                                                 |
   +=========================+=========================================================================================================================================+
   | **Processor**           | `Texas Instruments AM6232 <https://www.ti.com/product/AM623>`_                                                                          |
   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+
   | **SDRAM Memory**        | 512MB DDR4 (Kingston D2516AN9EXGXN-TU)                                                                                                  |
   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+
   | **PMIC**                | TPS6521903                                                                                                                              |
   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+
   | **Debug Support**       | 3 pin 3.3V JST-SH 1.00mm UART debug port (RPI debug probe compatible)                                                                   |
   +                         +-----------------------------------------------------------------------------------------------------------------------------------------+
   |                         | 10-pin JTAG TAG-CONNECT footprint                                                                                                       |
   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+
   | **Power Source**        | USB C or Cape Header VIN (5V @ 1A)                                                                                                      |
   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+
   | **PCB**                 | 55 x 35 mm                                                                                                                              |
   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+
   | **Indicators**          | 1x Power, 1x Battery charging, and 4x User Controllable LEDs                                                                            |
   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+
   | **SD/MMC Connector**    | microSD (1.8/3.3V)                                                                                                                      |
   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+
   | **User Input**          | 1. Power Button                                                                                                                         |
   |                         | 2. User/Boot Button                                                                                                                     |
   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+
   | **Weight**              | 12.7gm                                                                                                                                  |
   +-------------------------+-----------------------------------------------------------------------------------------------------------------------------------------+

.. _pocketbeagle-2-component-locations:

Board Component Locations
***************************

This section describes the key components on the board. It provides information on their location 
and function. Familiarize yourself with the various components on the board.

.. _pocketbeagle-2-components:

Board components
================

This section describes the key components on the board, their location and function.

.. tab-set::

   .. tab-item:: Front components location

      .. figure:: images/components/front.*
         :width: 1240
         :align: center
         :alt: PocketBeagle 2 board front components location
   
         PocketBeagle 2 board front components location

      .. table:: PocketBeagle 2 board front components location table
         :align: center
         
         +----------------------------+---------------------------------------------------------------------------+
         | Feature                    | Description                                                               |
         +============================+===========================================================================+
         | AM6232 SoC                 | Internet of Things (IoT) and gateway SoC with dual core A53 @ 1GHz        |
         +----------------------------+---------------------------------------------------------------------------+
         | MSPM0 MCU                  | MSPM0 MCU to provide ADC and EEPROM functionality                         |
         +----------------------------+---------------------------------------------------------------------------+
         | U, P and C LEDs            | USR1 - USR4 (U) user LEDs, Power (P) & Charging (C) LED indicator         |
         +----------------------------+---------------------------------------------------------------------------+
         | USB C                      | Power and connectivity.                                                   |
         +----------------------------+---------------------------------------------------------------------------+
         | User button                | User action button, hold down to boot from sdCard on a board with eMMC    |
         +----------------------------+---------------------------------------------------------------------------+
         | Power button               | Hold down to toggle ON/OFF                                                |
         +----------------------------+---------------------------------------------------------------------------+
         | TPS6521903                 | Power Management Integrated Circuit (PMIC)                                |
         +----------------------------+---------------------------------------------------------------------------+
         | 512MB RAM                  | 512MB DDR4 RAM                                                            |
         +----------------------------+---------------------------------------------------------------------------+
         | JTAG debug port            | Tag-Connect JTAG (AM6232) debug port                                      |
         +----------------------------+---------------------------------------------------------------------------+

   .. tab-item:: Back components location

      .. figure:: images/components/back.*
         :width: 1240
         :align: center
         :alt: PocketBeagle 2 board back components location

         PocketBeagle 2 board back components location

      .. table:: PocketBeagle 2 board back components location table
         :align: center

         +----------------------------+---------------------------------------------------------------------------+
         | Feature                    | Description                                                               |
         +============================+===========================================================================+
         | microSD                    | Micro SD Card holder                                                      |
         +----------------------------+---------------------------------------------------------------------------+
         | P1 & P2 cape header        | Expansion headers for PocketBeagle capes.                                 |
         +----------------------------+---------------------------------------------------------------------------+
         | UART debug ports           | 3pin JST-SH 1.00mm UART debug port (RPI debug probe compatible)           |
         +----------------------------+---------------------------------------------------------------------------+
 
