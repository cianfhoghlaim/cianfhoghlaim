.. _beagleboard-getting-started:

Getting Started Guide
#####################

Beagles are tiny computers ideal for learning and prototyping with electronics.
Read the step-by-step getting started tutorial below to begin developing with your Beagle in minutes.

.. _flash-latest-image:

Update board with latest software
************************************

This step may or may not be necessary, depending on how old a software image you already have,
but executing this step, the longest step, will ensure the rest will go as smooth as possible.

Download the latest software image
============================================

Download the latest software image from `beagleboard.org distros <https://www.beagleboard.org/distros>`_ page.
The "IoT" images provide more free disk space if you don't need to use a graphical user interface (GUI).

.. NOTE::
	Due to sizing necessities, this download may take 30 minutes or more.

1. `BeaglePlay latest image (xfce)`_
2. `BeaglePlay latest image (home-assistant)`_
3. `AM57xx latest image (IoT)`_ for BeagleBone AI and BeagleBone-X15
4. `AM57xx latest image (Xfce)`_ for BeagleBone AI and BeagleBone-X15
5. `BeagleBone AI-64 latest image (Minimal)`_
6. `BeagleBone AI-64 latest image (TI EDGEAI)`_
7. `BeagleBone AI-64 latest image (Xfce)`_
8. `AM335x latest image`_ for BeagleBone Black, PocketBeagle, BeagleBone Blue, etc.
9. `AM335x latest image (Xfce)`_ for BeagleBone Black, PocketBeagle, BeagleBone Blue, etc.
10. `AM335x latest image (IoT)`_ for BeagleBone Black, PocketBeagle, BeagleBone Blue, etc.
11. `BeagleConnect Freedom latest image (micropython)`_
12. `BeagleV-Ahead latest image (Ubuntu)`_
13. `BeagleV-Ahead latest image (Yocto)`_

The Debian/Ubuntu distribution is provided for the boards. The file you download will have an .img.xz extension.
This is a compressed sector-by-sector image of the SD card.

|image0|

Install SD card programming utility
=============================================

Download and install `balenaEtcher <https://www.balena.io/etcher/>`_.

|image1|
|image2|

Connect SD card to your computer
===========================================

Use your computer's SD slot or a USB adapter to connect the SD card to your computer.

Write the image to your SD card
=========================================

Use Etcher to write the image to your SD card. Etcher will transparently decompress the
image on-the-fly before writing it to the SD card.

|image3|

Eject the SD card
============================

Eject the newly programmed SD card.

Boot your board off of the SD card
============================================

Insert SD card into your (powered-down) board, hold down the USER/BOOT button
and apply power, either by the USB cable or 5V adapter.
	
If using an original BeagleBone or PocketBeagle, you are done.

.. note::
    If using BeagleBone Black, BeagleBone Blue, BeagleBone AI, BeagleBone AI-64, BeaglePlay or other board with on-board eMMC
    flash and you desire to write the image to your on-board eMMC, you'll need to follow the
    instructions at http://elinux.org/Beagleboard:BeagleBoneBlack_Debian#Flashing_eMMC.
    During flash all 4 USRx LEDs will show sequential chaser pattern. When the flashing is complete, all 4 USRx LEDs will be
    steady off and possibly power down the board upon completion. This can take up to 45 minutes.  Power-down your board,
    remove the SD card and apply power again to finish.

Start your Beagle
*****************

If any step fails, it is recommended to update to the
`latest software image <https://www.beagleboard.org/distros>`_
using the instructions above.

.. _board-power-and-boot:

Power and boot
================

Most Beagles can be powered via a USB cable, providing a convenient way to provide both power to your
Beagle and connectivity to your computer. Be sure the cable is of good quality and your source can provide enough power.

Alternatively, your Beagle may have a barrel jack which can take power from a wall adapter. 
Checkout :ref:`accessories-power-supplies` to get the correct adapter for your Beagle.

.. Danger::
	Make sure to use only a 5V center positive adapter for all Beagles except BeagleBone Blue and BeagleBoard-X15 (12V).

If you are using your Beagle with an `SD (microSD) card <https://en.wikipedia.org/wiki/Secure_Digital>`_, make sure it is inserted ahead of providing power.
Most Beagles include programmed on-board flash and therefore do not require an SD card to be inserted.

You'll see the power (PWR or ON) LED lit steadily. Within a minute or so, you should see the other LEDs
blinking in their default configurations. Consult your :ref:`boards` documentation to locate these LEDs.

- USR0 is typically configured at boot to blink in a heartbeat pattern.
- USR1 is typically configured at boot to light during SD (microSD) card accesses.
- USR2 is typically configured at boot to light during CPU activity.
- USR3 is typically configured at boot to light during eMMC accesses.
- USR4/WIFI is typically configured at boot to light with WiFi (client) network association (Only on boards with built-in WiFi or M.2).

Enable a network connection
============================

If connected via USB, a network adapter should show up on your computer.
Your Beagle should be running a DHCP server that will provide your computer
with an IP address of either 192.168.7.1 or 192.168.6.1, depending on the
type of USB network adapter supported by your computer's operating system.
Your Beagle will reserve 192.168.7.2 or 192.168.6.2 for itself.

If your Beagle includes WiFi, an access point called "BeagleBone-XXXX" will be created where "XXXX"
varies between boards. The access point password defaults to "BeagleBone". Your Beagle should be 
running a DHCP server that will provide your compute with an IP address in the 192.168.8.x range 
and reserve 192.168.8.1 for itself.

If your Beagle is connected to your local area network (LAN) via either Ethernet or WiFi,
it will utilize `mDNS <https://en.wikipedia.org/wiki/Multicast_DNS>`_ to broadcast itself
to your computer. If your computer supports mDNS, you should see your Beagle as ``beaglebone.local``.
Non-BeagleBone boards will utilize alternate names. Multiple BeagleBone boards on the same
network will add a suffix such as beaglebone-2.local.

.. _start-browse-to-beagle:

Browse to your Beagle
============================

A web server with an Visual Studio Code (IDE) should be running on your Beagle. 
Point your browser to `http://192.168.7.2:3000 <http://192.168.7.2:3000>`_ to begin development.

.. figure:: images/vscode.png
   :width: 920
   :align: center
   :alt: Visual Studio Code Server

   Visual Studio Code Server

.. note::
    Use either `Firefox <https://www.mozilla.org/firefox>`_ or `Chrome <https://www.google.com/chrome>`_
    (Internet Explorer will NOT work), browse to the web server running on your board. It will load a presentation
    showing you the capabilities of the board. Use the arrow keys on your keyboard to navigate the presentation.

The below table summarizes the typical addresses.

.. list-table::
    :header-rows: 1

    * - Link
      - Connection type
      - Operating System(s)
    * - http://192.168.7.2
      - USB
      - Windows
    * - http://192.168.6.2
      - USB
      - Mac OS X, Linux
    * - http://192.168.8.1
      - WiFi
      - all
    * - http://beaglebone.local
      - all
      - mDNS enabled
    * - http://beaglebone-2.local
      - all
      - mDNS enabled

Troubleshooting
***************

.. tip:: Do not use Internet Explorer.

Virtual machines are not recommended when using the direct USB connection.
It is recommended you use only network connections to your board if you are using a virtual machine.

.. note:: When using 'ssh' with the provided image, the username is '`debian`' and the password is '`temppwd`'.

With the latest images, it should no longer be necessary to install drivers for your operating
system to give you network-over-USB access to your Beagle. In case you are running an older image,
an older operating system or need additional drivers for serial access to older boards, links to the old drivers are below.

.. list-table::
    :header-rows: 1

    * - Operating system
      - USB Driver
      - Comments
    * - Windows (64-bit)
      - `64-bit installer <https://beagleboard.org/static/Drivers/Windows/BONE_D64.exe>`_
      - If in doubt, try the 64-bit installer first.
    * - Windows (32-bit)
      - `32-bit installer <https://beagleboard.org/static/Drivers/Windows/BONE_DRV.exe>`_
      -
    * - Mac OS X
      - `Network Serial <https://beagleboard.org/static/Drivers/MacOSX/FTDI/EnergiaFTDIDrivers2.2.18.pkg>`_
      - Install both sets of drivers.
    * - Linux
      - `mkudevrules.sh <https://beagleboard.org/static/Drivers/Linux/FTDI/mkudevrule.sh>`_
      - Driver installation isn't required, but you might find a few udev rules helpful.

.. Note::
	For Windows (64-bit):

	1. Windows Driver Certification warning may pop up two or three times. Click "Ignore", "Install" or "Run".
	2. To check if you're running 32 or 64-bit Windows see `this <https://support.microsoft.com/en-us/topic/determine-whether-your-computer-is-running-a-32-bit-version-or-64-bit-version-of-the-windows-operating-system-1b03ca69-ac5e-4b04-827b-c0c47145944b>`_.
	3. On systems without the latest service release, you may get an error (0xc000007b). In that case, please perform the following and retry: https://answers.microsoft.com/en-us/windows/forum/all/windows-10-error-code-0xc000007b/02b74e7d-ce19-4ba4-90f0-e16e8d911866
	4. You may need to reboot Windows.
	5. These drivers have been tested to work up to Windows 10


	Additional FTDI USB to serial/JTAG information and drivers are available from https://www.ftdichip.com/Drivers/VCP.htm

	Additional USB to virtual Ethernet information and drivers are available from http://www.linux-usb.org/gadget/ and https://joshuawise.com/horndis

	Visit https://docs.beagleboard.org/latest/intro/support/index.html for additional debugging tips.

Hardware documentation
**********************

Be sure to check check the latest hardware documentation for your board at https://docs.beagleboard.org. 
Detailed design materials for various boards can be found at https://git.beagleboard.org/explore/projects/topics/boards.

Books
*****

For a complete list of books on BeagleBone, see `beagleboard.org/books <https://beagleboard.org/books>`_.

|image8|

Perfect for high-school seniors or freshman univerisity level text, consider using "Bad to the Bone"

|image9|

A lighter treatment suitable for a bit broader audience without the backgrounders on programming and
electronics, consider "BeagleBone Cookbook"

|image10|

To take things to the next level of detail, consider "Exploring BeagleBone" which can be considered
the missing software manual.

|image11|

utilize "Embedded Linux Primer" as a companion textbook to provide
a strong base on embedded Linux suitable for working with any hardware that will run Linux.


.. |image0| image:: images/distros.png
   :width: 75.0%
.. |image1| image:: images/download-etcher.png
   :width: 75.0%
.. |image2| image:: images/install-etcher.png
   :width: 75.0%
.. |image3| image:: images/write-latestimage.png
   :width: 75.0%
.. |image4| image:: images/btn_step1.gif
   :class: steps
.. |image5| image:: images/btn_step2.gif
   :class: steps
.. |image6| image:: images/btn_step3.gif
   :class: steps
.. |image7| image:: images/bone101.png
   :width: 600px
   :target: http://192.168.7.2
.. |image8| image:: images/bad-to-the-bone.jpg
   :target: https://bbb.io/bad-to-the-bone
.. |image9| image:: images/beaglebone-cookbook.jpg
   :target: https://bbb.io/cookbook
.. |image10| image:: images/exploring-beaglebone.jpg
   :target: https://bbb.io/ebb
.. |image11| image:: images/embedded-linux-primer.jpg
   :target: https://bbb.io/elp
