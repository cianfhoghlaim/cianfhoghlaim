.. _bbai-quick-start:

Quick start
###########

What’s In the Box
*****************

BeagleBone® AI comes in the box with the heat sink and antenna already
attached. Developers can get up and running in five minutes with no
microSD card needed. BeagleBone® AI comes preloaded with a Linux
distribution. In the box you will find:

-  `BeagleBone® AI <https://www.beagleboard.org/boards/beaglebone-ai>`_
-  Quick Start Guide

.. image:: images/BB_AI_antenna_heat_sink_place_500px.jpg
   :align: center
   :alt: BeagleBone AI Overview

.. tip:: For board files, 3D model, regulatory docs and more, you can checkout `BeagleBona-AI repository on OpenBeagle <https://openbeagle.org/beagleboard/beaglebone-ai/>`_.

What’s Not in the Box
**********************

You will need to purchase:

-  :ref:`USB C cable or USB C to USB A cable <accessories-cables-usb>`
-  MicroSD Card (optional)
-  :ref:`Serial cable <molex-picoblade-serial-cables>` (optional)

More information or to purchase a replacement heat sink or antenna, please go to these websites:

-  `Antenna <https://bit.ly/2kmXAzF>`_
-  `Heat Sink <https://bit.ly/2klxxJa>`_

Fans
*****

The pre-attached heat sink has M3 holes spaced 20x20 mm. The height of
the heat sink clears the USB type A socket, and all other components on
the board except the 46-way header sockets and the Ethernet socket.

If you run all of the accelerators or have an older software image,
you’ll likely need fan. To find a fan, visit the link to `fans in the
FAQ <https://git.beagleboard.org/beagleboard/beaglebone-ai/-/wikis/Frequently-Asked-Questions#fans>`_.

.. caution::

   BeagleBone AI can run **HOT**! Even without running the accelerators,
   getting up to 70C is not uncommon.

   Read about `Fan update for BeagleBone AI on Forum 
   <https://forum.beagleboard.org/t/fan-update-for-beaglebone-ai/1964>`. 

1. `Official BeagleBone Fan Cape <https://www.newark.com/element14/6100310/beaglebone-ai-fan-cape/dp/50AH3704>`_
2. `Coolerguys 25mm (25x25x10) USB Fan <https://www.coolerguys.com/en-in/collections/usb-fans/products/25mm-25x25x10-usb-fan>`

Main Connection Scenarios
**************************

This section will describe how to connect the board for use. The board
can be configured in several different ways. Below we will walk through
the most common scenarios. NOTE: These connection scenarios are
dependent on the software image presently on your BeagleBone® AI. When
all else fails, follow the instructions at :ref:`upgrade-beaglebone-ai-software`.

- Tethered to a PC via USB C cable
- Standalone Desktop with powered USB hub, display, keyboard and mouse
- Wireless Connection to BeagleBone® AI

.. tab-set:: 

    .. tab-item:: Tethered

      **Tethered to a PC**

      The most common way to program BeagleBone® AI is via a USB connection to
      a PC. If your computer has a USB C type port, BeagleBone® AI will both
      communicate and receive power directly from the PC. If your computer
      does not support USB C type, you can utilize a powered USB C hub to
      power and connect to BeagleBone® AI which in turn will connect to your
      PC. You can also use a powered USB C hub to power and connect peripheral
      devices such as a USB camera. After booting, the board is accessed
      either as a USB storage device or via the browser on the PC. You will
      need Chrome or Firefox on the PC.

      .. note:: Start with this image "am57xx-eMMC-flasher-debian-10.3-iot-tidl-armhf-2020-04-06-6gb.img.xz" loaded on your BeagleBone® AI.

      1.  Locate the USB Type-C connector on BeagleBone® AI 

      .. image:: images/BB_AI_USBC_and_3pin_500px.png
         :width: 740
         :align: center
         :alt: USB connector and serial debug.

      2.  Connect a USB type-C cable to BeagleBone® AI USB type-C port.

      .. image:: images/BB_AI_connectingUSBC_500px.jpg
         :width: 740
         :align: center
         :alt: Connecting serial cable.

      3.  Connect the other end of the USB cable to the PC USB 3 port.

      .. image:: images/BB_AI_PlugIn_500px.jpg
         :width: 740
         :align: center
         :alt: connecting to PC

      4.  BeagleBone® AI will boot.

      5.  You will notice some of the 5 user LEDs flashing

      6.  Look for a new mass storage drive to appear on the PC.

      .. image:: images/BB_AI_asadrive_500px.jpg
         :width: 740
         :align: center
         :alt: BeagleBone storage drive options

      7.  Open the drive and open START.HTM with your web browser.

      .. image:: images/BB_AI_starthtm_500px.png
         :width: 740
         :align: center
         :alt: BeagleBone drive 

      .. image:: images/BB_AI_connectedscreen_500px.jpg
         :width: 740
         :align: center
         :alt: Getting started

      8.  Follow the instructions in the browser window.

      .. image:: images/vscode.png
         :width: 740
         :align: center
         :alt: BeagleBone instructions

      9.  Go to Visual Studio Code IDE.
    
    .. tab-item:: Standalone

      **Standalone w/Display and Keyboard/Mouse**

      .. image:: images/BB_AI_Standalone_setup_750px.jpg
         :width: 740
         :align: center
         :alt: BeagleBone AI Overview

      .. note::
          This configuration requires loading the latest debian 9 image from
          https://elinux.org/Beagleboard:Latest-images-testing

      Load "am57xx-eMMC-flasher-debian-9.13-lxqt-tidl-armhf-2020-08-25-6gb.img.xz" image on the BeagleBone® AI

      10. Connect a combo keyboard and mouse to BeagleBone® AI’s USB host port.
      11. Connect a microHDMI-to-HDMI cable to BeagleBone® AI’s microHDMI port.
      12. Connect the microHDMI-to-HDMI cable to an HDMI monitor.
      13. Plug a 5V 3A USB type-C power supply into BeagleBone® AI’s USB type-C port.
      14. BeagleBone® AI will boot. No need to enter any passwords.
      15. Depending on which software image is loaded, either a Desktop or a login shell will appear on the monitor.
      16. Follow the instructions at https://beagleboard.org/upgrade

    .. tab-item:: Wireless

      **Wireless Connection**

      .. note:: Start with this image "am57xx-eMMC-flasher-debian-10.3-iot-tidl-armhf-2020-04-06-6gb.img.xz" loaded on your BeagleBone® AI.

      17. Plug a 5V 3A USB type-C power supply into BeagleBone® AI’s USB type-C port.
      18. BeagleBone® AI will boot.
      19. Connect your PC’s WiFi to SSID "BeagleBone-XXXX" where XXXX varies for your BeagleBone® AI.
      20. Use password "BeagleBone" to complete the WiFi connection.
      21. Open http://192.168.8.1 in your web browser.
      22. Follow the instructions in the browser window.

Connecting a 3 PIN Serial Debug Cable
*************************************

A 3 PIN serial debug cable can be helpful to debug when you need to view
the boot messages through a terminal program such as putty on your host
PC. This cable is not needed for most BeagleBone® AI boot up scenarios.

Cables: https://git.beagleboard.org/beagleboard/beaglebone-ai/-/wikis/Frequently-Asked-Questions#serial-cable

Locate the 3 PIN debug header on BeagleBone® AI, near the USB C connection.

.. image:: images/BB_AI_USBC_and_3pin_500px.png
   :align: center
   :alt: BeagleBone AI Overview

Press the small white connector into the 3 PIN debug header. The pinout is:

- Pin 1 (the pin closest to the screw-hole in the board. It is also marked with a shape on the silkscreen): GND
- Pin 2: UART1_RX (i.e. this is a BB-AI input pin)
- Pin 3: UART1_TX (i.e. BB-AI transmits out on this pin)

.. image:: images/BB_AI_3pincableattach_500px.jpg
   :align: center
   :alt: BeagleBone AI Overview
