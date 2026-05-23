.. _beaglev-fire-gateware-design:

Gateware Design Introduction
############################

The PolarFire SoC device used on BeagleV-Fire is an SoC FPGA which includes a RISC-V processors
subsystem and a PolarFire FPGA on the same die. The gateware configures the Microcprosessor
subsystem's hardware and programs the FPGA with digital logic allowing customization of the use of
BeagleV-Fire connectors.

Gateware Architecture
=====================

The diagram below is a simplified overview of the gateware's structure.

.. figure:: images/Gateware-Flow-simplified-overview.*
    :align: center
    :alt: BeagleV-Fire Simplified Gateware

    
The overall gateware is made-up of several blocks, some of them interchangeable. These blocks are
all clocked and reset by another "Clock and Resets" block not showed in the diagram for clarity. A 125MHz,
and a 160MHz clock are provided for use by the gateware blocks.

Each gateware block is associated with one of BeagleV-Fire's connectors.

All gateware blocks have an AMBA APB target interface for software to access control and status registers
defined by the gateware to operate digital logic defined by the gateware block. This is the
software's control path into the gateware block.

Some gateware blocks also have an AMBA AXI target and/or source interfaces. The AXI interfaces are
typically used to move high volume of data at high throughput in and out of DDR memory. For example,
the M.2 gateware uses these interfaces to transfer data in and out of its PCIe root port.

Cape Gateware
-------------
The cape gateware handles the P8 and P9 connectors signals. This is where support for specific capes is
implemented.

This is a very good place to start learning about FPGA and how to customize gateware.


SYZYGY Gateware
---------------
The SYZYGY gateware handles the high-speed connector signals. This connector includes:
 - up to three transceivers capable of 12.7Gbps communications
 - One SGMII interface
 - 10 high-speed I/Os
 - Clock inputs

There is a lot of fun that can be had with this interface given its high-speed capabilities.

Please note that only two tranceivers can be used when the M.2 interface is enabled.

MIPI-CSI Gateware
-----------------
The MIPI gateware handles the signals coming from the camera interface.

Gateware for the MIPI-CSI interface is Work-In-Progress.


M.2 Gateware
------------
The M.2 gateware implements the PCIe interface used for Wi-Fi modules. It connects the processor subsystem
to the PCIe controller associated with the tranceivers bank.

There is limited fun to have here. You either include this block or not in your bitstream.

The M.2 gateware uses one of the four available 12.7 Gbps transceivers. Only two out of the three SYZYGY
tranceivers can be used when the M.2 is included in the bitstream. This gateware needs to omited from
the bitstream if you want to use all three 12.7Gbps transceivers on the SYZYGY high-speed connector.

RISC-V Processors subsystem
---------------------------
The RISC-V Processors Subsystem also includes some gateware mostly dealing with exposing AMBA bus interfaces
for the other gateware blocks to attach to. It also handles immutable aspects of the gateware related to how
some PolarFire-SoC signals are used to connect BeagleV-Fire peripherals such as the ADC and EEPROM.
As such the RISC-V Processors Subsystem gateware is not intended to be customized.





