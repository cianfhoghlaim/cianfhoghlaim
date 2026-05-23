.. _beagley-ai-introduction:

Introduction 
#############

BeagleY-AI is an open-source single board computer designed for edge AI applications.

.. image:: images/beagley-ai-board.*

.. _beagley-ai-detailed-overview:

Detailed overview
******************

BeagleY-AI is based on the Texas Instruments AM67A Arm-based vision processor.  It features a quad-core 64-bit Arm®Cortex®-A53 CPU subsystem at 1.4GHz, 
Dual general-purpose C7x DSP with Matrix Multiply Accelerator (MMA) capable of 4 TOPS (trillion-operations per second) combined (2 TOPS each), two available 800MHz Arm Cortex-R5 subsystems for low-latency 
I/O and control, a 50 GFlop GPU, video and vision accelerators, and other specialized processing capability.

.. table:: BeagleY-AI features
        
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Feature               | Description                                                                                                                                             |
    +=======================+=========================================================================================================================================================+
    | Processor             | Texas Instruments AM67A, Quad 64-bit Arm® Cortex®-A53 @1.4 GHz, multiple cores including Arm/GPU processors, DSP, and vision/deep learning accelerators |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | RAM                   | 4GB LPDDR4 (x32)                                                                                                                                        |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Wi-Fi/Bluetooth       | BeagleBoard.org BeagleMod BM3301, 802.11ax Wi-Fi 6, Bluetooth Low Energy (BLE) 5.4                                                                      |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | USB Ports             | 4 x USB 3.0 TypeA ports supporting simultaneous 5Gbps operation, 1 x USB 2.0 TypeC, supports USB 2.0 device mode                                        |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Ethernet              | Gigabit Ethernet, with PoE+ support (requires separate PoE HAT)                                                                                         |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Camera/Display        | 2 x 4-lane MIPI camera connector (one connector muxed with DSI capability)                                                                              |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Display Output        | 1 x HDMI display, 1 x OLDI display, 1 x DSI MIPI Display (DSI muxed with 1 CSI)                                                                         |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Real-time Clock (RTC) | Supports external coin-cell battery for power failure time retention                                                                                    |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Debug UART            | 1 x 3-pin debug UART                                                                                                                                    |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Power                 | 5V/3A DC power via USB-C                                                                                                                                |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Power Button          | On/Off included                                                                                                                                         |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | PCIe Interface        | PCI-Express® Gen3 x 1 interface for fast peripherals (requires separate M.2 HAT or other adapter)                                                       |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Expansion Connector   | 40-pin header                                                                                                                                           |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Fan connector         | 1 x 4-pin fan connector, supports PWM control and fan speed measurement                                                                                 |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Storage               | microSD card slot with UHS-1 support                                                                                                                    |  
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Tag Connect           | 1 x JTAG, 1 x External PMIC programming port                                                                                                            |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+

.. _AM67A: https://www.ti.com/product/AM67A

AM67A SoC
=========

The `AM67A`_ scalable processor family is based on the evolutionary Jacinto™ 7 architecture, targeted at Smart
Vision Camera and General Compute applications and built on extensive market knowledge accumulated over
a decade of TI’s leadership in the Vision processor market. The `AM67A`_ family is built for a broad set of
cost-sensitive high performance compute applications in Factory Automation, Building Automation, and other
markets.

Some Applications include:

- Human Machine Interface (HMI)
- Hospital patient monitoring
- Industrial PC
- Building security system
- Off-highway vehicle
- Test and measurement
- Energy storage systems
- Video Surveillance
- Machine Vision
- Industrial mobile robot (AGV/AMR)
- Front camera systems



The `AM67A`_ provides high performance compute technology for both traditional and deep learning algorithms
at industry leading power/performance ratios with a high level of system integration to enable scalability and
lower costs for advanced vision camera applications. Key cores include the latest Arm and GPU processors for
general compute, next generation DSP with scalar and vector cores, dedicated deep learning and traditional
algorithm accelerators, an integrated next generation imaging subsystem (ISP), video codec, and MCU cores. All
protected by industrial-grade security hardware accelerators.

.. tip:: For more information about AM67A SoC you can checkout https://www.ti.com/product/AM67A

Board components location
***************************

Front components
=================

.. figure:: images/components-location/beagley-ai-board-front-annotated.*
    :width: 1400
    :align: center
    :alt: BeagleY-AI board front components location 

.. table:: BeagleY-AI board front components location
    :align: center

    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | Feature              | Description                                                                                                       |
    +======================+===================================================================================================================+
    | WiFi/Bluetooth       | BeagleBoard.org BeagleMod BM3301 with 802.11ax Wi-Fi 6 & Bluetooth Low Energy 5.4 (BLE)                           |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | RAM                  | 4GB LPDDR4 (x32)                                                                                                  |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | Expansion            | 40pin Expansion header compatible with HATs                                                                       |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | SoC                  | TI AM67A Arm®Cortex®-A53 4 TOPS vision SoC with RGB-IR ISP for 4 cameras, machine vision, robotics, and smart HMI |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | Fan                  | 4-pin fan connector                                                                                               |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | USB-A                | 4 x USB 3 TypeA ports supporting simultaneous 5Gbps operation host ports                                          |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | Network Connectivity | Gigabit Ethernet                                                                                                  |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | PoE                  | Power over Ethernet HAT connector                                                                                 |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | Camera/Display       | 1 x 4-lane MIPI camera/display transceivers, 1 x 4-lane MIPI camera                                               |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | Debug UART           | 1 x 3-pin JST-SH 1.0mm debug UART port                                                                            |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | Display Output       | 1 x HDMI display                                                                                                  |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | USB-C                | 1 x Type-C port for power, and supports USB 2 device                                                              |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | PMIC                 | Power Management Integrated Circuit for 5V/5A DC power via USB-C with Power Delivery support                      |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | Bicolor LED          | Indicator LED                                                                                                     |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | Power button         | ON/OFF button                                                                                                     |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+
    | PCIe                 | PCI-Express® Gen3 x 1 interface for fast peripherals (requires separate M.2 HAT or other adapter)                 |
    +----------------------+-------------------------------------------------------------------------------------------------------------------+

Back components
================

.. figure:: images/components-location/beagley-ai-board-back-annotated.*
    :width: 1400
    :align: center
    :alt: BeagleY-AI board back components location 

.. table:: BeagleY-AI board back components location
    :align: center

    +----------------+-----------------------------------------------------------+
    | Feature        | Description                                               |
    +================+===========================================================+
    | Tag-Connect    | 1 x JTAG & 1 x Tag Connect for PMIC NVM Programming       |
    +----------------+-----------------------------------------------------------+
    | Display output | 1 x OLDI display                                          |
    +----------------+-----------------------------------------------------------+
    | Storage        | microSD card slot with support for high-speed SDR104 mode |
    +----------------+-----------------------------------------------------------+
