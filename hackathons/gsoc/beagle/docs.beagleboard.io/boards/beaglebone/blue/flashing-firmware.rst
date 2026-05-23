.. _beaglebone-blue-flashing-firmware:

Flashing Firmware
#####################

Overview
*********

Most Beaglebones have a built in 4 GB SD card known as a eMMC (embedded
MMC). When the boards are made the eMMC is “flashed” with some version
of the BeagleBone OS that is usually outdated. Therefore, whenever
receiving the BeagleBone it is recommend that you update the eMMC with
the last version of the BeagleBone OS or a specific version of it if
someone tells you otherwise.

Required Items
****************

1. Micro sd card. 4 GB minimum
2. Micro sd card reader or a built in sd card reader for your PC
3. BeagleBone image you want to flash.
4. `Etcher utility <https://etcher.io/>`_ for your PC’s OS.

Steps Overview
****************

1. Burn the image you want to flash onto a micro sd card using the
   Etcher utility.
2. Boot the BeagleBone like normal and place the micro sd card into the
   board once booted.
3. Update the micro sd card image so its in “flashing” mode.
4. Insert micro sd card, remove power from the BeagleBone, hold sd card
   select button, power up board
5. Let the board flash

Windows PCs
=============

1.  Download the `BeagleBone
    OS <https://www.beagleboard.org/distros>`_ image you want to use.
2.  Use the `Etcher utility <https://etcher.io/>`_ to burn the
    BeagleBone image you want to use on the micro sd card you plan on
    using.
3.  Make sure you don’t have the micro sd card plugged into your board.
4.  Boot the board
5.  Connect to the board via serial or ssh so that your on the command
    prompt.
6.  Plug the micro sd card into the board.
7.  Type dmesg in the terminal window
8.  The last line from the output should say something like (the
    numbering may differ slightly):

    -  ``"[ 2805.442940]  mmcblk0: p1"``

9.  You want to take the above and combine it together by removing the :
    and space. For the above example it will change to “mmcblk0p1”
10. In the terminal window enter the following commands:

.. code:: bash

   mkdir sd_tmp
   sudo mount /dev/mmcblk0p1 sd_tmp
   sudo su
   echo "cmdline=init=/opt/scripts/tools/eMMC/init-eMMC-flasher-v3.sh" >> sd_tmp/boot/uEnv.txt
   exit
   sudo umount sd_tmp

11. Now power off your board
12. Hold the update button labeled ``SD`` (the one by itself) to boot
    off the sdcard.
13. Restart (RST button) or power up (while still pushing SD button).

Flashing can take some minutes. 

Linux/Mac PCs 
=============

1.  Download the
    `BeagleBone OS <https://www.beagleboard.org/distros>`_ image you want
    to use. 
2.  Use the `Etcher utility <https://etcher.io/>`_ to burn the
    BeagleBone image you want to use on the micro sd card you plan on using.
3.  On the SD card edit the file ``/boot/uEnv.txt`` in order for the SD
    card contents to be flashed onto the firmware eMMC. (Otherwise the BBBL
    will do no more than boot the SD image.) Uncomment the line containing
    ``init-eMMC-flasher-v<number>.sh`` either manually or using these
    commands substituting ``X`` with what your SD card shows in ``/dev/``:

.. code:: bash

   sudo mount /dev/emmcblkXp1 /mnt
   cd /mnt
   sed -i 's_#[ ]*\(cmdline=init=/opt/scripts/tools/eMMC/init-eMMC-flasher-v[0-9]\+.*\.sh\)_\1_' boot/uEnv.txt

4.  Eject the sdcard from your computer.
5.  Put it into your BeagleBoneBlue.
6.  If your board was already powered on then power it off
7.  Hold the update button labeled ``SD`` (the one by itself) to boot off
    the sdcard.
8.  Restart (RST button) or power up (while still pushing SD button).

Flashing can take some minutes.

How to tell if it is flashing?
-------------------------------

At first a blue heartbeat is shown indicating the image is booted. On
flash procedure start, the blue user LEDs light up in a “larson scanner”
or “cylon” pattern (back and forth).

When finished, either all blue LEDs are on or the board is already
switched off.

If the LEDs are on for a long time then it may indicate failure
e.g. wrong image. Can be verified if boot fails, i.e. board turns off
again shortly after power up.
