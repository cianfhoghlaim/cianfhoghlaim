.. _beagley-ai-expansion-nvme:

Booting from NVMe Drives
##########################

.. todo:: Add further testing steps, results, and images.

BeagleY-AI supports a PCI-Express x1 interface which enables data rates of up to 1GB/s for high speed expansion. 

.. note:: While the SoC supports PCI-e Gen 3, the flat-flex connector required by HATs is only rated for PCI-e Gen 2, so, as is the case with other similar boards in this form factor, actual transfer speeds may be limited to Gen 2, depending on a variety of layout and environmental factors

This enables it to take advantage of standard PC NVMe drives which offer exponentially higher random and sequential read/write speeds as well as improved endurance over SD cards or traditional eMMC storage.

While the boot-ROM on the AM67 SoC does not support direct boot-to-NVMe, we can use a method where we boot U-Boot from the SD Card and then use it to load the Linux filesystem from external NVMe storage. 

Verified HATs and Drives
***************************

Most/All HATs and NVMe drives should work, but the following have been verified to work as part of writing this guide:

HATs:

1. `Geekworm X1001 PCIe to M.2 Key-M <https://www.amazon.com/Geekworm-X1001-Key-M-Peripheral-Raspberry/dp/B0CPPGGDQT>`_
2. `Geekworm X1000 PCIe M.2 Key-M <https://www.amazon.com/gp/product/B0CQ4D2C9S>`_

NVMe drives:

1. `Kingston OM3PDP3512B (512GB 2230) <https://www.amazon.com/Kingston-512GB-3-0x4-Solid-OM3PDP3512B-A01/dp/B0BW7V8ZZ3>`_
2. `Kingston NV2 (512GB 2280) <https://www.amazon.com/Kingston-500G-2280-Internal-SNV2S/dp/B0BBWJH1P8/>`_

Drive Adapters (3D Printable):

The X1000 above uses the slightly uncommon 2242 drive size, so, an adapter may be required to mount a 2230 drive. 

1. A simple adapter from ``@eliasjonsson`` on Printables works great - https://www.printables.com/model/578236-m2-ssd-2230-to-2242 
2. Similar adapters exist for 2230 to 2280 for example such as this one from ``@nzalog`` - https://www.printables.com/model/217264-2230-to-2280-m2-adapter-ssd

Step by step
************

.. note:: This article was written using the `BeagleY-AI Debian XFCE 12.5 2024-06-12 image <https://www.beagleboard.org/distros/beagley-ai-debian-12-5-2024-06-12-xfce/>`_.

Step 1. Boot from SD Normally
===============================

Grab the latest BeagleY-AI SD Image from (`BeagleBoard.org/distros <https://www.beagleboard.org/distros>`_.) 

Once logged in and at the terminal, make sure your system is up to date (a reboot is also recommended after updating)

.. code:: console

    sudo apt-get update && sudo apt-get full-upgrade -y
    sudo reboot


Step 2. Verify that your NVMe drive is detected
=================================================

The command ``lspci`` will list the attached PCI Express devices on the system:

.. code:: console

    debian@BeagleY:~$ lspci

You should see an output similar to the following, where the first entrance is the SoC internal PCI Express bridge device and the second device listed is your NVMe drive, in this case, a Kingston OM3PDP3 drive.

.. code:: console

    00:00.0 PCI bridge: Texas Instruments Device b010
    01:00.0 Non-Volatile memory controller: Kingston Technology Company, Inc. OM3PDP3 NVMe SSD (rev 01)

Now that we know the PCIe device is detected, let's see if it's recognized as a Storage Device:

The command ``lsblk`` will list the attached storage devices on the system:

.. code:: console

    debian@BeagleY:~$ lsblk
    NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
    mmcblk1     179:0    0 29.7G  0 disk
    ├─mmcblk1p1 179:1    0  256M  0 part /boot/firmware
    ├─mmcblk1p2 179:2    0    4G  0 part [SWAP]
    └─mmcblk1p3 179:3    0 25.5G  0 part /
    nvme0n1     259:0    0 476.9G  0 disk
    └─nvme0n1p1 259:1    0 476.9G  0 part

Here we see that two devices are connected, ``mmcblk1`` corresponds to our SD card, and ``nvme0n1`` corresponds to our NVMe drive, so everything is ready to go!


If your drives aren't listed as expected, please check the Troubleshooting section at the end of this document. 

Step 3a. Transfer your root filesystem over to NVMe with a bootmenu option (recommended)
==========================================================================================
For this method, you will need `Raspberry Pi Debug Probe <https://www.raspberrypi.com/documentation/microcontrollers/debug-probe.html>`_ 
or similar serial (USB to UART) adapter, to select the ``2: transfer microSD rootfs to NVMe (advanced)`` the boot menu option:

.. code:: console

    Scanning mmc 1:1...
    Found /extlinux/extlinux.conf
    Retrieving file: /extlinux/extlinux.conf
    BeagleY-AI microSD (extlinux.conf) (swap enabled)
    1:	microSD (production test)
    2:	transfer microSD rootfs to NVMe (advanced)
    3:	microSD (debug)
    4:	microSD (default)
    Enter choice: 2

The BeagleY-AI will shutdown when complete


Step 3b. Transfer your root filesystem over to NVMe with a shell script
========================================================================

A variety of useful scripts are available  in ``/opt/``, one of them enables us to move our micro-sd contents to NVMe and make BeagleY-AI boot from there directly.

The following 3 commands will change your U-boot prompt to boot from NVMe by default, but the serial boot menu will still enable you to fall back to SD boot or other modes if something happens.

.. note:: This will copy the entire contents of your SD card to the NVMe drive, so expect it to take upwards of 15 minutes. This only needs to be run one time

.. code:: console

    sudo cp -v /opt/u-boot/bb-u-boot-beagley-ai/beagley-ai-microsd-to-nvme-w-swap /etc/default/beagle-flasher

.. code:: console

    sudo beagle-flasher-mv-rootfs-to-nvme

.. code:: console

    sudo reboot


Step 4. (optional) Verify u-boot (Serial Debug) will jump to the rootfs on the NVMe
=====================================================================================

.. note:: boot menu ``1: return to microSD`` will allow you to return to the microSD rootfs for any reasons.

.. code:: console

    Scanning mmc 1:1...
    Found /extlinux/extlinux.conf
    Retrieving file: /extlinux/extlinux.conf
    BeagleY-AI NVMe (extlinux.conf) (swap enabled)
    1:	return to microSD
    2:	NVMe (debug)
    3:	NVMe (default)
    Enter choice: 3


Enjoy NVMe speeds!
==================

Now that we've run the scripts above, you should see that lsblk now reports that our ``/`` or root filesystem is on the ``nvme0n1p1`` partition, meaning we are successfully booting from the NVMe drive.

It's subtle, but the change can be seen by running ``lsblk`` again.

.. code:: console

    debian@BeagleY:~$ lsblk
    NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
    mmcblk1     179:0    0  29.8G  0 disk
    ├─mmcblk1p1 179:1    0   256M  0 part /boot/firmware
    ├─mmcblk1p2 179:2    0     4G  0 part
    └─mmcblk1p3 179:3    0  25.6G  0 part
    nvme0n1     259:0    0 931.5G  0 disk
    ├─nvme0n1p1 259:1    0     4G  0 part [SWAP]
    └─nvme0n1p2 259:2    0 927.5G  0 part /

Congratulations! 

Troubleshooting
********************

While most setups should work, it is possible that a combination of Software, Hardware or both can result in minor issues. Here are some ideas for troubleshooting on your own:

Check that your cables are plugged in and oriented correctly
============================================================

The flat-flex ribbon cable will only connect correctly one way, so ensure the orientation is correct with your expansion HAT manual and that the ribbon cable is correctly seated. 

A note on power-hungry drives
=============================

While most drives can be powered as-is with only the ribbon cable, some drives, especially high end full-size 2280 drives may consume more power than normal for an M.2 connector. 
For such cases, some HAT expansions will provide a means of providing external supplemental power. If your drive is not detected, it may be worthwhile to try using a drive from a different manufacturer as a troubleshooting step.

As a side note, since 2230 drives are normally designed to run in Laptops, they tend to also consume less power than their desktop counterparts and as such, are a "safer" option.

Check the Linux Kernel Logs for PCI:
====================================

You should see something similar to below without further errors:

.. code:: console

    debian@BeagleY:~$ dmesg | grep "PCI"
    [    0.005276] PCI/MSI: /bus@f0000/interrupt-controller@1800000/msi-controller@1820000 domain created
    [    0.158546] PCI: CLS 0 bytes, default 64
    [    3.674209] j721e-pcie-host f102000.pcie: PCI host bridge to bus 0000:00
    [    3.742406] pci 0000:01:00.0: 7.876 Gb/s available PCIe bandwidth, limited by 8.0 GT/s PCIe x1 link at 0000:00:00.0 (capable of 31.504 Gb/s with 8.0 GT/s PCIe x4 link)
    [    4.915630] pci 0000:00:00.0: PCI bridge to [bus 01]


Still having issues? 
====================

Post questions on the `forum under the tag "beagley-ai" <https://forum.beagleboard.org/tags/c/general/8/beagley-ai>`_.
