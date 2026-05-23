.. _beagley-ai-design:

Design and Specifications
#########################

.. todo:: Add details about all the schematic sections.

If you want to know how BeagleY-AI is designed and the detailed specifications, then
this chapter is for you. We are going to attempt to provide you a short and crisp overview
followed by discussing each hardware design element in detail.

.. tip:: For board files, 3D model, and more, you can checkout the `BeagleY-AI repository on OpenBeagle <https://openbeagle.org/beagley-ai/beagley-ai>`_.

Block Diagram and Overview
***************************

.. figure:: images/hardware-design/beagley-ai-block-diagram.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI block diagram

    BeagleY-AI block diagram

Processor
**************

.. figure:: images/am67a.png
    :align: center
    :alt: AM67A block diagram

    AM67A block diagram

The AM67A processor from Texas Instruments is a highly integrated SoC with an Automotive pedigree. It may be referenced by TI documentation
by it's superset J722s/TDA4AEN. 

It's primary compute cluster revolves around 4xARM Cortex-A53 Cores running at 1.4Ghz. 

An MCU subsystem consisting of an ARM Cortex-R5F running at up to 800Mhz is also available for user applications and is especially useful
for real-time IO applications. 

For very advanced users, two additional R5 cores are also present, but they are normally reserved for Device and Run-time Management of the SoC typically. 

2x C7x DSPs with MMA support are intended for use as Deep Learning Accelerators for things like AI Vision, with up to 2TOPS each. 

An Imagination BXS-4-64 GPU rounds out the compute cluster, with a dedicated video encoder/decoder available for multimedia tasks. 

The SoC features advanced high speed connectivity, including USB3.1, PCIe and more.  

Secure Boot is also available with the ability burn One-Time-Programmable (OTP) eFUSES by energizing the VPP test pads.

Boot Modes
***********

.. figure:: images/hardware-design/beagley-ai-boot-modes.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI boot modes

    BeagleY-AI boot modes

The default boot mode for BeagleY-AI is the SD Card Interface. If no SD card is present, the BootROM on the AM67A SoC is going to try booting from Ethernet.

It is also possible to load U-Boot from the SD card and then load your main file system from another source, such as :ref:`beagley-ai-expansion-nvme`.

Power
***************

.. figure:: images/hardware-design/beagley-ai-pdn.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI power distribution network

    BeagleY-AI power distribution network

BeagleY-AI's power architecture is split between the TPS65219 PMIC which handles the main logic rails and a dedicated TPS62872 high current buck regulator for the SoC core rail which defaults to 0.85V on boot. 

Both PMIC and VDD_CORE regulators are highly configurable but will boot the board to "sane" defaults out of box. For advanced users, it is possible to adjust both the VDD_CORE rail as well as IO rails (voltages, timings, behavior, etc.) for applications such as low power modes where
you may want to trade clock speeds for power efficiency by running the SoC Core at 0.75V for example. Be careful, as changes here could result in unexpected behavior, the board not booting or even hardware damage, so tread carefully.

.. note:: At the time of writing, dynamic voltage switching is not supported by the AM67A SoC.

Clocks and Resets
*********************

.. figure:: images/hardware-design/beagley-ai-reset-cntrls-mcu-osc.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC Reset, Cntrls, and Clk

    BeagleY-AI SoC Reset, Cntrls, and Clk

BeagleY's main clock source is a 25Mhz Crystal Oscillator connected to MCU_OSC0 pins.

.. figure:: images/hardware-design/beagley-ai-wkup-reset-cntrls-osc.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI wkup reset cntrls osc

    BeagleY-AI wkup reset cntrls osc

A 32.768Khz "Slow Clock" Crystal is used on the WKUP_LFOSC0 domain. 

USB-C Power/Data Port
------------------------------

.. figure:: images/hardware-design/beagley-ai-usb-c.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI USB-C

    BeagleY-AI USB-C


The board is powered via USB-C, using 5.1 kΩ resistors to signal itself as a power sink (UFP) and enable 5V output.
It assumes 500 mA by default (per USB-C’s "Power Sinking Device" rules) but requires 5V @ 3A for stable operation. 
The USB-C source dictates available current (via CC-line signaling), which the board does not validate. Users must 
ensure their charger explicitly supports 3A. While USB-PD supplies default to 5V, they may not deliver 3A unless the 
source advertises it, risking instability or port damage if undersourced.

The USB-C port also functions as a USB 2.0 device, providing serial console access, Ethernet gadget connectivity, 
and USB Mass Storage (UMS) emulation. A Type-C to Type-C cable is recommended to avoid power limitations, and 
unpowered hubs should be avoided. single-cable design simplifies connectivity but relies on proper power sourcing.
Inadequate behavior may result in brownouts/resets or other unexpected behavior. 

PMIC
----------------

.. figure:: images/hardware-design/beagley-ai-pmic.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI PMIC

    BeagleY-AI PMIC


HCPS (High Current Power Stage)
---------------------------------

.. figure:: images/hardware-design/beagley-ai-vdd-core-hcps.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI VDD core High Current Power Stage (HCPS)

    BeagleY-AI VDD core High Current Power Stage (HCPS)

Analog Rail Decoupling
------------------------------------

.. figure:: images/hardware-design/beagley-ai-soc-analog-power1.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC analog power1

    BeagleY-AI SoC analog power rail decoupling capacitors

.. figure:: images/hardware-design/beagley-ai-soc-io-ddr-power2.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI AI SoC IO and DDR power2

    BeagleY-AI AI SoC IO and DDR decoupling capacitors

Digital Rail Decoupling
-----------------------------------------

.. figure:: images/hardware-design/beagley-ai-soc-digital-power3.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC digital power3

    BeagleY-AI SoC VDD & VDDR_CORE decoupling capacitors

.. note:: Other power sections are nested within their specific interface section. 

LDOs
----------

.. figure:: images/hardware-design/beagley-ai-vsys-3v3.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI VSYS 3V3

    BeagleY-AI VSYS 3V3

While the 3.3V VDD_IO rail is provided by the PMIC, the actual "high current" VSYS 3.3V rail used on the expansion header and elsewhere 
in the system is provided by a discrete TPS62A06DRLR regulator. 

.. figure:: images/hardware-design/beagley-ai-ethernet-power-3v3-to-2v5.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI ethernet power 3V3 to 2V5

    BeagleY-AI ethernet power 3V3 to 2V5

The 2V5 Rail used by the Ethernet PHY is generated a discrete TPS74801 regulator. 
This regulator is fed by the 3V3 VSYS regulator.  


.. figure:: images/hardware-design/beagley-ai-3v3-2v5-to-1v1-ldo.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI 3V3/V5 to 1V1 LDO

    BeagleY-AI 3V3/V5 to 1V1 LDO

The 1V1 Rail used by the PHY and USB 3.1 Hub is generated a discrete TPS74801 regulator. 
By default, this regulator is fed by the 3V3 VSYS regulator previously discussed.

Memory
****************************

RAM (LPDDR4)
--------------

.. figure:: images/hardware-design/beagley-ai-ddr.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI DDR

    BeagleY-AI DDR

BeagleY-AI has 4GB of Kingston x32 LPDDR4 Memory. 

.. todo:: Add Final DDR Part Number

.. figure:: images/hardware-design/beagley-ai-soc-ddr0.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC DDR0 connections

    BeagleY-AI SoC DDR0 connections

.. figure:: images/hardware-design/beagley-ai-ddr-caps.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI DDR caps

    BeagleY-AI DDR caps

.. figure:: images/hardware-design/beagley-ai-ddr-power.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI DDR power

    BeagleY-AI DDR power

EEPROM
--------------

.. figure:: images/hardware-design/beagley-ai-board-id-eeprom.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI board id eeprom

    BeagleY-AI board id eeprom

BeagleY-AI features an on-board FT24C32A 32Kbit I2C EEPROM for storing things like board information, manufacture date, etc. 

.. todo:: Add details about specific EEPROM contents and formatting.

microSD Card
--------------
.. figure:: images/hardware-design/beagley-ai-micro-sd-card-interface.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI microSD card interface

    BeagleY-AI microSD card interface

The microSD card is the primary boot interface for BeagleY-AI, it corresponds to the MMC1 interface on the AM67A SoC. 

To enable UHS-1 SD card functionality (and speeds!), a load switch is provided which allows the SoC MMC1 PHY to switch the SD Card IO voltage to 1.8V.

.. todo:: Explain UHS-1 in more detail and add link to TRM for boot modes and resistor swap options for advanced users.

General Expansion
************************************

40pin Header
--------------------

.. figure:: images/hardware-design/beagley-ai-user-expansion-connector.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI user expansion connector

    BeagleY-AI user expansion connector

BeagleY-AI features a 40-pin GPIO Header which aims to enable compatibility with a lot of existing Raspberry Pi HAT add-on boards. 
See `pinout.beagleboard.io <https://pinout.beagleboard.io/>`_ for a more comprehensive view of the 40 pin GPIO header,
available pin functions and tested accessories!

.. todo:: Add link to docs on building expansion accessories. 

I2C
---------------

.. figure:: images/hardware-design/beagley-ai-iic-tree.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI I2C tree

    BeagleY-AI I2C tree

By default, 5 different I2C interfaces are exposed, all of which feature external 2.2KΩ pull-up resistors. 3 of the interfaces are used by the CSI, DSI and OLDI ports for Cameras & Displays.
The remaining 2 ports are exposed on the 40pin GPIO expansion connector. 

The MCU_I2C0 interface is intended as the primary external I2C interface for BeagleY-AI and matches physical pins 3 and 5 of the header. Most HATs will use these pins. 

While WKUP_I2C0 is also exposed on the 40pin Header (physical pins 27 & 28), that bus is shared with several on-board devices, namely the PMIC, VDD_CORE regulator, Board ID EEPROM and RTC. As such,
it is highly advisable to leave these pins unused unless you are sure you know what you are doing. These pins are normally only pinned out as a "HAT EEPROM detect" for RPi HATs that provide such functionality (of which there are very few)

See `pinout.beagleboard.io/pinout/i2c <https://pinout.beagleboard.io/pinout/i2c>`_  for a more visual explanation. 

.. figure:: images/hardware-design/beagley-ai-iic-voltage-level-translator.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI voltage level translator

    BeagleY-AI voltage level translator

USB
---------

.. figure:: images/hardware-design/beagley-ai-usb3-hub.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI USB3 hub

    BeagleY-AI USB3 hub

BeagleY-AI features a USB3.1 HUB that provides 4 total USB3.1 Ports from a single USB3.1 Gen-1 (5 Gbps) SERDES0
lane.

.. figure:: images/hardware-design/beagley-ai-usb-hub-config.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI USB hub config

    BeagleY-AI USB hub config

.. figure:: images/hardware-design/beagley-ai-soc-serdes0.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC SERDES0

    BeagleY-AI SoC SERDES0

.. figure:: images/hardware-design/beagley-ai-soc-usb0-and-usb1.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC USB0 and USB1

    BeagleY-AI SoC USB0 and USB1

.. figure:: images/hardware-design/beagley-ai-dual-usb-1.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI USB-A Connector 1

    BeagleY-AI USB-A Connector 1

.. figure:: images/hardware-design/beagley-ai-dual-usb-2.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI USB-A Connector 2

    BeagleY-AI USB-A Connector 2

.. figure:: images/hardware-design/beagley-ai-dual-usb-current-limiter.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI dual USB current limiter

    BeagleY-AI dual USB current limiter

BeagleY-AI features a dedicated USB current limiter that will prevent the Type-A ports from drawing
power in excess of 2.8A.

.. figure:: images/hardware-design/beagley-ai-usb-vbus-resistor-divider-circuit.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI USB VBUS resistor divider circuit

    BeagleY-AI USB VBUS resistor divider circuit

PCI Express
---------------

.. figure:: images/hardware-design/beagley-ai-pcie-connector.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI PCIE connector

    BeagleY-AI PCIE connector

BeagleY-AI features an RPi 5 compatible PCIe connector rated for PCIe Gen2 x1 (5GT/s) connected to SERDES1 on AM67A. 

.. note:: Just like the Raspberry Pi 5, while the AM67A SoC is capable of PCIe Gen3 (8GT/s), the choice of cable/connector means that some devices may not be able to run at full Gen 3 speeds and will need to be limited to Gen 2 for stable operation.

.. figure:: images/hardware-design/beagley-ai-soc-serdes1.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC SERDES1

    BeagleY-AI SoC SERDES1

RTC (Real-time Clock)
------------------------

.. figure:: images/hardware-design/beagley-ai-iic-ext-rtc.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI I2C ext RTC

    BeagleY-AI I2C ext RTC

BeagleY-AI has an on-board I2C RTC that can be powered by an external RTC for accurate time-keeping even when the board is powered off.
For more information, see the corresponding docs page - :ref:`beagley-ai-using-rtc` 


Fan Header
------------------------

.. figure:: images/hardware-design/beagley-ai-fan-connector.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI fan connector

    BeagleY-AI fan connector

BeagleY-AI features a Raspberry Pi 5 compatible Fan connector. The fan is software PWM controller in Linux by default 
to maintain a balance between cooling and noise depending on SoC temperature.

Networking
************

WiFi / Bluetooth LE
------------------------------

.. figure:: images/hardware-design/beagley-ai-wifi-module.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI WiFi module

    BeagleY-AI WiFi module

.. figure:: images/hardware-design/beagley-ai-soc-mmc-012.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC MMC0, MMC1, and MMC2

    BeagleY-AI SoC MMC0, MMC1, and MMC2


BeagleY-AI features a Beagle BM3301 Wireless module based on the Texas Instruments CC3301 which features 2.4Ghz WiFi6 (802.11AX) and BLE 5.4

.. note:: 5Ghz WiFi Bands and Bluetooth Classic are not supported by the CC3301.

Ethernet
------------------------------

BeagleY-AI is equipped with a 1 Gb (10/100/1000) DP83867 Ethernet PHY connected over RGMII.

.. figure:: images/hardware-design/beagley-ai-ethernet-dp83867.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI ethernet DP83867

    BeagleY-AI ethernet DP83867

.. figure:: images/hardware-design/beagley-ai-ethernet-connector.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI ethernet connector
    
    BeagleY-AI ethernet connector

BeagleY-AI uses an RJ45 ethernet connector with integrated magnetics. 

.. figure:: images/hardware-design/beagley-ai-soc-rgmii.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC RGMII

    BeagleY-AI SoC RGMII

.. figure:: images/hardware-design/beagley-ai-rgmii-rst.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC RGMII1 RST

    BeagleY-AI SoC RGMII1 RST

.. figure:: images/hardware-design/beagley-ai-ethernet-phy-caps.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI ethernet PHY caps

    BeagleY-AI Ethernet PHY caps

.. figure:: images/hardware-design/beagley-ai-ethernet-phy-misc.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI ethernet phy misc

    BeagleY-AI Ethernet PHY misc

.. figure:: images/hardware-design/beagley-ai-ethernet-phy-protection.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI ethernet phy protection

    BeagleY-AI Ethernet PHY protection

.. figure:: images/hardware-design/beagley-ai-poe-header.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI PoE header

    BeagleY-AI PoE header

Optional PoE (Power over Ethernet) can also be used with compatible 3rd party HATs designed for the Raspberry Pi 5.

.. note:: Only Pi 5 PoE HATs are compatible, as Pi 4 and previous designs have the PoE pins in a different location.   

Cameras & Displays
***********************

BeagleY-AI is capable of driving up to 3 Displays (HDMI, OLDI/LVDS & DSI) simultaneously.

* HDMI via DPI Converter up to 1920 x 1080 @60FPS
* OLDI/LVDS up to 3840 x 1080 @60FPS (Dual Link, 150-Mhz Pixel Clock)
* DSI up to 3840 x 1080 at 60fps (4 Lane MIPI® D-PHY, 300-MHz Pixel Clock)

It also features 2 CSI interfaces and can support up to 8 Cameras using Virtual Channels and V3Link. 

.. note:: The CSI1/DSI0 22-pin port is muxed between the two interfaces like the RPi 5, meaning that you must chose if it's used as a Display or Camera port. The CSI0 22-pin connector can only be used as a Camera port.   

HDMI (DPI)
-----------------

.. figure:: images/hardware-design/beagley-ai-rgb888-to-hdmi.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI RGB888 to HDMI

    BeagleY-AI RGB888 to HDMI

BeagleY-AI has a single HDMI 1.4 port capable of up to 1080p @60FPS with Audio. This is achieved
using an external Parallel RGB (DPI) to HDMI converter from ITE. 

Because the DPI interface is used up by the HDMI converter, it does mean that DPI is not available on the 40Pin GPIO header.

.. figure:: images/hardware-design/beagley-ai-soc-vout.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC VOUT

    BeagleY-AI SoC VOUT

.. figure:: images/hardware-design/beagley-ai-hdmi-addr-protection.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI HDMI addr protection

    BeagleY-AI HDMI addr protection

.. figure:: images/hardware-design/beagley-ai-hdmi-power.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI HDMI power

    BeagleY-AI HDMI power

.. figure:: images/hardware-design/beagley-ai-hdmi-reset.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI HDMI reset

    BeagleY-AI HDMI reset

OLDI (LVDS)
-----------------

.. figure:: images/hardware-design/beagley-ai-soc-oldi.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC OLDI

    BeagleY-AI SoC OLDI

The OLDI connector on BeagleY-AI has the same pinout as the one used by Beagle Play, meaning the same displays
are compatible. 

DSI
-----------------

.. figure:: images/hardware-design/beagley-ai-soc-dsi.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC DSI connections

    BeagleY-AI SoC DSI0 TX connections

The DSI0 port is shared withe CSI1 and selectable via a MUX switch to maintain Pi functionality. It features the same
pinout found on the 22-pin DSI connector on RPi5 and BeagleBone AI-64 and enables connectivity to existing supported DSI displays.

.. figure:: images/hardware-design/beagley-ai-rpi-dsi-csi.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI RPI DSI/CSI

    BeagleY-AI RPI DSI/CSI

Please note that DSI is only available on the second of the two 22-pin "CSI" connectors. 

CSI
-----------------

.. figure:: images/hardware-design/beagley-ai-rpi-csi.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI RPI CSI

    BeagleY-AI RPI CSI

To maintain a Pi compatible form factor, BeagleY-AI only exposes 2 of the 4 physical CSI interfaces of the AM67A SoC. 
Each CSI interfaces is MIPI® CSI-2 v1.3 + MIPI® D-PHY 1.2 with 4 Data Lanes running at up to 2.5Gbps/lane. 
The interface also supports up to 16 Virtual Channels for multi-camera applications using FPDLink or V3Link. 

.. figure:: images/hardware-design/beagley-ai-soc-csi-0123.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC CSI1, CSI2, and CSI3

    BeagleY-AI SoC CSI1, CSI2, and CSI3

Buttons and LEDs
*****************

.. figure:: images/hardware-design/beagley-ai-leds.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI LEDs

    BeagleY-AI LEDs

BeagleY-AI features a single dual-color (Red/Green) LED for Power/Status indication.

Debug Ports
************

JTAG Tag-Connect
-------------------

.. figure:: images/hardware-design/beagley-ai-tag-connect.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI Tag-Connect

    BeagleY-AI Tag-Connect

JTAG is available on the BeagleY-AI via a 10pin Tag-Connect header located on the bottom of the board between the USB 3.0 ports. 

Because of the density of the board and tight fit of the USB connectors, the standard retention clip provided by Tag-Connect will not fit.
A recommended 3D printable adapter is `available on Printables <https://www.printables.com/model/879533-beagley-ai-tagconnect-clip-10pin>`_ 

UART
-------------------

.. figure:: images/hardware-design/beagley-ai-debug-uart-port.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI debug UART port

    BeagleY-AI debug UART port

By default, BeagleY-AI exposes the UART port used by UBoot & Linux on a Pi Debugger compatible JST 3pin header. The UART port used for debug
can also be changed in software to use a UART available on the 40Pin GPIO header.

PMIC NVM Tag-Connect
--------------------------------------

.. figure:: images/hardware-design/beagley-ai-pmic-nvm-programming.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI PMIC NVM programming interface

    BeagleY-AI PMIC NVM programming interface

A PMIC programming header is present on the BeagleY-AI in the form of a 10pin Tag-Connect header located on the bottom of the board between the Ethernet and USB 3.0 ports.
Ensure you do not connect JTAG to this port as the pinout and interface is different. PMIC NVM programming should not be performed unless
you know what you're doing. The port is mainly intended for use during manufacturing. 


Miscellaneous
********************

.. figure:: images/hardware-design/beagley-ai-general-io.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI general IO

    BeagleY-AI general IO

.. figure:: images/hardware-design/beagley-ai-mcu-general-io.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI MCU general IO

    BeagleY-AI MCU general IO

.. figure:: images/hardware-design/beagley-ai-soc-ospi.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC OSPI0

    BeagleY-AI SoC OSPI0

.. figure:: images/hardware-design/beagley-ai-soc-efuse-vmon-jtag-rsvd.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC eFUSE, VMON, Debug, and RSVD

    BeagleY-AI SoC eFUSE, VMON, Debug, and RSVD

.. figure:: images/hardware-design/beagley-ai-soc-gpmc.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC GPMC0

    BeagleY-AI SoC GPMC0

.. figure:: images/hardware-design/beagley-ai-soc-supply-noise-kelvin-sensing.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC supply noise kelvin sensing

    BeagleY-AI SoC supply noise kelvin sensing

.. figure:: images/hardware-design/beagley-ai-soc-ground.*
    :width: 1040
    :align: center
    :alt: BeagleY-AI SoC ground connections

    BeagleY-AI SoC ground connections

Mechanical Specifications 
**************************

.. todo::

   If there are real design elements, put those here, like clearances and other elements going
   into design consideration. Summary information should just go in the support page.

Dimensions & Weight
===================

.. table:: Dimensions & weight

    +--------------------+----------------------------------------------------+
    | Parameter          | Value                                              |
    +====================+====================================================+
    | Size               | 85 x 56 x 20 mm                                    |
    +--------------------+----------------------------------------------------+
    | Max heigh          | 20mm                                               |
    +--------------------+----------------------------------------------------+
    | PCB Size           | 85 x 56 mm                                         |
    +--------------------+----------------------------------------------------+
    | PCB Layers         | 14 layers                                          |
    +--------------------+----------------------------------------------------+
    | PCB Thickness      | 1.6mm                                              |
    +--------------------+----------------------------------------------------+
    | RoHS compliant     | Yes                                                |
    +--------------------+----------------------------------------------------+
    | Gross Weight       | 110 g                                              |
    +--------------------+----------------------------------------------------+
    | Net Weight         | 50 g                                               |
    +--------------------+----------------------------------------------------+
