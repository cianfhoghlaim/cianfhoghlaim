.. _beaglev-fire-upgrade-gateware:

Upgrade BeagleV-Fire Gateware
####################################

This document describes how to upgrade your BeagleV-Fire's gateware. This approach can be used out
of the box using Linux commands executed on BeagleV-Fire

Required Equipment
********************
- BeagleV-Fire board
- USB-C cable
- Ethernet cable

The USB-C cable provides power, a serial interface to BeagleV-Fire and allows connecting to
BeagleV-Fire through a browser using IP address ``192.168.7.2``.

The Ethernet cable connected to your local network (LAN) allows connecting to BeagleV-Fire using
the SSH protocol. It also allows BeagleV-Fire to retrieve updated packages through your local
network's Internet connection.

Connect to BeagleV-Fire Linux Command Line Interface
*****************************************************
BeagleV-Fire boots Linux out of the box. Like all Beagleboard boards there are several methods to
get BeagleV-Fire's Linux command prompt.

- Cockpit
- SSH
- Serial port

Cockpit
========

Enter the following URL in your web browser: ``https://beaglev.localdomain:9090/``

On first use, click through the security warning. Login using ``beagle/temppwd`` as user/password.
Click on Terminal in the left pane. You now have a Linux command prompt running on your
BeagleV-Fire. Next step: enter the commands described in the Gateware Upgrade Linux Commands
section of this document.

.. note::
    
    You can connect to the Cockpit using the IP address dynamically assigned to your
    BeagleV-Fire in your local Ethernet network. One method of finding the value of that
    dynamically assigned IP address is to open a serial terminal though the USB port and use the
    ``ip address`` Linux command. Please refer to the USB Serial Port section.

SSH
====

Like all Beagleboard boards, you can SSH to the board through the USB interface by using IP
address 192.168.7.2.

.. note::
    
    On Windows, this approach may require some drivers to be updated or installed. Use one of the
    other approaches if you are not immediately successful with this one. You can circle back later
    to adjust your Windows installation if required.

Serial Port
================

A serial port is available through the USB-C port. This serial port becomes available once Linux
has booted on BeagleV-Fire. Please wait a couple of minutes after powering up the board before
looking for additional serial ports reported by your host computer's operating system. You can then
use your favorite serial port terminal tool such as Putty or Screen to access the BeagleV-Fire
Linux command prompt.

For example on your Linux host computer:

.. code-block:: shell

    screen /dev/ttyACM0 115200

Where ``ttyACM0`` is an additional serial port that appeared after BeagleV-Fire was connected to
your Linux host computer. This serial port can be identified using the ``dmesg | grep tty`` Linux
command which will show the most recent serial port added to the host computer.

On Windows, BeagleV-Fire's serial port number will show in the Windows Device Manager. Use that
serial port number in Putty with a speed 115200 baud, no flow-control.

Gateware Upgrade Linux Commands
********************************

.. note::
    
    BeagleV-Fire needs to be connected to the internet through your local network for the commands
    in this section to work. The connection can be through the Ethernet port or the Wi-Fi module.

Install bbb.io-gateware
========================

You need to install the bbb.io-gateware package. This will allow retrieving the most up-to-date
gateware.

.. code-block:: shell

    sudo apt install bbb.io-gateware

Retrieve Available Updated Linux packages List
===============================================

The list will include the latest BeagleV-Fire gateware packages.

.. code-block:: shell

    sudo apt update

Upgrade Linux Packages
=======================

This will upgrade the BeagleV-Fire gateware Linux programming files located
under ``/usr/share/beagleboard/gateware``. Several directories are found in that location, each
containing programming files for one individual gateware configuration.

.. code-block:: shell

    sudo apt upgrade

Launch Reprogramming of BeagleV-Fire's FPGA
============================================

Change directory to ``/usr/share/beagleboard/gateware``. This directory contains a script
performing the gateware's reprogramming. It also contains one directory for each of the possible
gateware configuration that can be programmed into your BeagleV-Fire. The name of one of these
directories is passed as argument to the script to specify which gateware configuration you wish to
program your BeagleV-Fire with.

.. code-block:: shell

    cd /usr/share/beagleboard/gateware
    . ./change-gateware.sh default

.. important:: 
    Do not power-off BeagleV-Fire until it has rebooted by itself. The gateware reprogramming may
    take a couple of minutes.
    
The change-gateware script programs the selected gateware and its associated device tree overlays
into the PolarFire SoC System Controllers SPI flash and triggers a software reboot. During the
reboot, the Hart Software Services (HSS) will request the PolarFire SoC System Controller to
reprogram the FPGA and eNVM. The PolarFire SoC System Controller will reprogram the FPGA if it
finds it contains a different design version than the one in the SPI Flash. The board reboots on
completion of the FPGA reprogramming.
