.. _beaglebone-cookbook-basics:

Basics
#######

When you buy BeagleBone Black, pretty much everything you need to get going comes with it. 
You can just plug it into the USB of a host computer, and it works. The goal of this 
chapter is to show what you can do with your Bone, right out of the box. It has enough 
information to carry through the next three chapters on sensors (:ref:`beaglebone-cookbook-sensors`), 
displays (:ref:`beaglebone-cookbook-displays`), and motors (:ref:`beaglebone-cookbook-motors`).

Picking Your Beagle
=====================

Problem
--------

There are many different BeagleBoards. How do you pick which one to use?

Solution
---------

Check out the current list of boards: :ref:`boards`

.. _basics_out_of_the_box:

Getting Started, Out of the Box
================================

Problem
--------

You just got your Bone, and you want to know what to do with it.

Solution
---------

Many of the Beagles (:ref:`beagley-all-home`, :ref:`beagleplay-home`, 
:ref:`bbai64-home`, :ref:`bbai-home`, :ref:`beaglev-ahead-home` and
:ref:`beaglev-fire-home`)
have their own detailed **Quick start** guide.  Here we present
general instructions that work for all Beagles. 
Fortunately, you have all you need to get running: your Bone and a USB cable. 
Plug the USB cable into your host computer (Mac, Windows, or Linux) and plug the 
mini-USB connector side into the USB connector near the Ethernet connector on 
the Bone, as shown in :ref:`basics_pluggingIn_fig`.

.. _basics_pluggingIn_fig:

.. figure:: figures/pluggingIn.*
   :align: center
   :alt: Plugging BeagleBone Black into a USB port
   
   Plugging BeagleBone Black into a USB port

The four blue **USER LEDs** will begin to blink, and in 10 or 15 seconds, you'll see 
a new USB drive appear on your host computer. :ref:`basics_01gettingStarted_fig` 
shows how it will appear on a Windows host, and Linux and Mac hosts will look similar. 
The Bone acting like a USB drive and the files you see are located on the Bone.

.. _basics_01gettingStarted_fig:

.. figure:: figures/01GettingStarted.png
   :align: center
   :alt: A new USB drive
   
   The Bone appears as a USB drive

.. _basics_open_vsc:

Browse to http://192.168.7.2:3000 from your 
host computer (:ref:`basics_05gettingStarted_fig`). If the page is not found, run the following:

.. code-block:: shell-session

    bone$ sudo systemctl start bb-code-server.service

Wait a minute and try the URL again.

.. _basics_05gettingStarted_fig:

.. figure:: figures/05GettingStartedVScode.png
   :align: center
   :alt: Visual Studio Code

   Visual Studio Code

Here, you'll find *Visual Studio Code*, a web-based integrated development environment (IDE) 
that lets you edit and run code on your Bone!  See :ref:`basics_vsc` for more details.

.. WARNING:: 
    Make sure you turn off your Bone properly. 
    It's best to run the *halt* command:

   .. code-block:: bash
      
      bone$ sudo halt

      The system is going down for system halt NOW! (pts/0)
    
   This will ensure that the Bone shuts down correctly. If you just pull the power, 
   it is possible that open files would not close properly and might become corrupt.

Discussion
-----------

The rest of this book goes into the details behind this quick out-of-the-box demo. 
Explore your Bone and then start exploring the book.

.. _basics_latest_os:

Verifying You Have the Latest Version of the OS on Your Bone
=============================================================

Problem
--------

You just got BeagleBone Black, and you want to 
know which version of the operating system it's running.

Solution
---------

.. todo 
   update version

This book uses `Debian <https://www.debian.org>`_, the Linux distribution that currently ships on the Bone. 
However this book is based on a newer version (BeagleBoard.org Debian Bullseye IoT Image 2023-06-03) 
than what is shipping at the time of this writing. You can see which version your Bone is running by 
following the instructions in :ref:`basics_out_of_the_box` to log into the Bone.  Then run:

.. code-block:: bash

    bone$ cat /etc/dogtag
    BeagleBoard.org Debian Bookworm Minimal Image 2024-09-11

I'm running the **2024-09-11** version.

Running the Python Examples
===========================

Problem
--------

You'd like to learn Python to interact with the Bone to 
perform physical computing tasks without first learning Linux.

.. note:: 

   There are many JavaScript examples too, but they may not be as up to date as the Python examples.

Solution
---------

Plug your board into the USB of your host computer and browse to 
http://192.168.7.2:3000 using Google Chrome or Firefox (as shown in 
:ref:`basics_out_of_the_box`). In the left 
column, click on *examples*, then *BeagleBone* and then *Black*. 
Several sample scripts will appear.  Go and explore them.

.. todo
   examples are no longer on the board.


.. tip::

    Explore the various demonstrations of Python and JavaScript. These are what come with the Bone. 
    In :ref:`basics_repo` you see how to load the examples for the Cookbook.

.. _basics_repo:

Cloning the Cookbook Repository
================================

Problem
-------

You want to run the Cookbook examples.

Solution
--------

Connect your Bone to the Internet and log into it.  From the command line run:

.. code-block::

    bone$ git clone https://git.beagleboard.org/beagleboard/beaglebone-cookbook-code
    bone$ cd beaglebone-cookbook-code
    bone$ ls

You can look around from the command line, or explore from Visual Sudio Code. 
If you are using VSC, go to the *File* menu and select *Open Folder ...* and 
select beaglebone-cookbook-code. Then explore.

.. _basics_wire_breadboard:

Wiring a Breadboard
====================

Problem
--------

You would like to use a breadboard to wire things to the Bone.

Solution
---------

Many of the projects in this book involve interfacing things to the Bone. 
Some plug in directly, like the USB port.  Others need to be wired. If it's simple, 
you might be able to plug the wires directly into the *P8* or *P9* headers. 
Nevertheless, many require a breadboard for the fastest and simplest wiring. 

To make this recipe, you will need:

- Breadboard and jumper wires

The :ref:`basics_breadboard_template` shows a breadboard wired to the Bone. 
All the diagrams in this book assume that the ground pin (*P9_1* on the Bone) is wired to the 
negative rail and 3.3 V (*P9_3*) is wired to the positive rail.

.. _basics_breadboard_template:

Breadboard wired to BeagleBone Black
-------------------------------------

.. figure:: figures/template_bb.png
   :align: center
   :alt: Breadboard
   
   Breadboard wired to BeagleBone Black

.. _basics_vsc:

Editing Code Using Visual Studio Code
======================================

Problem
--------

You want to edit and debug files on the Bone.

Solution
---------

Plug your Bone into a host computer via the USB cable. Open a browser 
(either Google Chrome or FireFox will work) on your host computer 
(as shown in :ref:`basics_out_of_the_box`). After the Bone has booted up, 
browse to http://192.168.7.2:3000 on your host. You will see something 
like :ref:`basics_05gettingStarted_fig`.

Click the *examples* folder on the left and then click *BeagleBoard* and then *Black*, 
finally double-click ``seqLEDs.py``. You can now edit the file. 

.. note:: 

   If you edit lines 33 and 37 of the ``seqLEDs.py`` file (time.sleep(0.25)), 
   changing *0.25* to *0.1*, the LEDs next to the Ethernet port on your 
   Bone will flash roughly twice as fast.

.. _basics_vsc_IDE:

Running Python and JavaScript Applications from Visual Studio Code
===================================================================

Problem
--------

You have a file edited in VS Code, and you want to run it.

Solution
---------

VS Code has a *bash* command window built in at the bottom of the window. 
If it's not there, hit Ctrl-Shift-P and then type *terminal create new* 
then hit *Enter*.  The terminal will appear at the bottom of the screen.
You can run your code from this window. To do so, add 
``#!/usr/bin/env python`` at the top of the file that you want to run and save.

.. tip:: 
   If you are running JavaScript, replace the word **python** in the line with **node**.

At the bottom of the VS Code window are a series of tabs (:ref:`basics_vscBash_fig`). 
Click the *TERMINAL* tab. Here, you have a command prompt.

.. _basics_vscBash_fig:

.. figure:: figures/vscBash.png
   :align: center
   :alt: Visual Studio Code showing bash terminal

   Visual Studio Code showing bash terminal

Change to the directory that contains your file, make it executable, and then run it:

.. code-block:: bash

    bone$ cd ~/examples/BeagleBone/Black/
    bone$ ./seqLEDs.py


The *cd* is the change directory command. After you *cd*, 
you are in a new directory. Finally, *./seqLEDs.py* instructs the 
python script to run. You will need to press ^C (Ctrl-C) to stop your program.

.. _basics_find_image:

Finding the Latest Version of the OS for Your Bone
----------------------------------------------------

Problem
************

You want to find out the latest version of Debian that is available for your Bone.

Solution
************

.. tab-set::

   .. tab-item:: bb-imager

      The easiest way to see what the current images are and update your SD card
      is to use **bb-imager**.  :ref:`beagley-ai-bb-imager` gives details on how to us it.

   .. tab-item:: forum

      Another way to see the available images is to visit the beagleboard forum. 

      On your host computer, open a browser and go to https://forum.beagleboard.org/tag/latest-images 
      This shows you a list of dates of the most recent Debian images (:ref:`basics_deb1`).

      .. todo::

         Update for 2023-06-03

      .. _basics_deb1:

      .. figure:: figures/deb1.png
         :align: center
         :alt: Latest Debian images

         Latest Debian images

      At the time of writing, we are using the *Bullseye* image.  
      Click on its link. Scrolling up you'll find :ref:`basics_deb2`. 
      There are three types of snapshots, Minimal, IoT and Xfce Desktop. 
      IoT is the one we are running.

      .. _basics_deb2:

      .. figure:: figures/deb2.png
         :align: center
         :alt: Latest Debian images

         Latest Debian images

      These are the images you want to use if you are flashing a Rev C BeagleBone Black 
      onboard flash, or flashing a 4 GB or bigger miscroSD card. The image beginning 
      with *am335x-debian-11.3-iot-* is used for the non-AI boards. The one beginning 
      with *am57xx-debian-* is for programming the Beagle AI's.

      .. note::
         The onboard flash is often called the *eMMC* memory. We just call it *onboard flash*, but you'll 
         often see *eMMC* appearing in filenames of images used to update the onboard flash.

      Click the image you want to use and it will download. 
      The images are some 500M, so it might take a while.

.. _basics_install_os:

Running the Latest Version of the OS on Your Bone
==================================================

Problem
--------

You want to run the latest version of the operating system on your 
Bone without changing the onboard flash.

Solution
---------

This solution is to flash an external microSD card and run the Bone from it. 
If you boot the Bone with a microSD card inserted with a valid boot image, 
it will boot from the microSD card. If you boot without the microSD card 
installed, it will boot from the onboard flash.  

.. tip:: 

   If you want to reflash the onboard flash memory, see :ref:`basics_onboard_flash`.

.. note:: 

   I instruct my students to use the microSD for booting. I suggest they 
   keep an extra microSD flashed with the current OS. If they mess up the 
   one on the Bone, it takes only a moment to swap in the extra microSD, 
   boot up, and continue running. If they are running off the onboard flash, 
   it will take much longer to reflash and boot from it.

Download the image you found in :ref:`basics_find_image`. It's more than 500 MB, 
so be sure to have a fast Internet connection. Then go to http://beagleboard.org/getting-started#update and 
follow the instructions there to install the image you downloaded.

Updating the OS on Your Bone
=============================

Problem
--------

You've installed the latest version of Debian on your Bone 
(:ref:`basics_install_os`), and you want to be sure it's up-to-date.

Solution
---------

Ensure that your Bone is on the network and then run the 
following command on the Bone:

.. code-block:: bash

    bone$ sudo apt update
    bone$ sudo apt upgrade

If there are any new updates, they will be installed.

.. note:: 

   If you get the error *The following signatures were invalid: KEYEXPIRED 1418840246*, 
   see `eLinux support page <http://bit.ly/1EXocb6>`_ for advice on how to fix it.

Discussion
-----------

After you have a current image running on the Bone, it's not at all difficult to keep it upgraded.

Backing Up the Onboard Flash
=============================

.. todo 
   keep?

Problem
--------

You've modified the state of your Bone 
in a way that you'd like to preserve or share.  Note, this doesn't apply to boards that
don't have onboard flash (PocketBeagle and BeagleY-AI).

Solution
---------

The `eLinux wiki <http://elinux.org/Beagleboard>`_ page on `BeagleBone Black Extracting eMMC contents <http://bit.ly/1C57I0a>`_
provides some simple steps for copying the contents of the onboard flash to a file on a microSD card:

- Get a 4 GB or larger microSD card that is FAT formatted.
- If you create a FAT-formatted microSD card, you must edit the partition and ensure that it is a bootable partition.
- Download `beagleboneblack-save-emmc.zip <http://bit.ly/1wtXwNP>`_ and uncompress and copy the contents onto your microSD card.
- Eject the microSD card from your computer, insert it into the powered-off BeagleBone Black, and apply power to your board.
- You'll notice *USER0* (the LED closest to the S1 button in the corner) will (after about 20 seconds) begin to blink steadily, rather than the double-pulse "heartbeat" pattern that is typical when your BeagleBone Black is running the standard Linux kernel configuration.
- It will run for a bit under 10 minutes and then *USER0* will stay on steady. That's your cue to remove power, remove the microSD card, and put it back into your computer.
- You will see a file called *BeagleBoneBlack-eMMC-image-XXXXX.img*, where *XXXXX* is a set of random numbers. Save this file to use for restoring your image later.

.. note:: 

   Because the date won't be set on your board, you might want to 
   adjust the date on the file to remember when you made it. For 
   storage on your computer, these images will typically compress 
   very well, so use your favorite compression tool.

.. tip:: 

   The `eLinux wiki <http://elinux.org/Beagleboard>`_ is the 
   definitive place for the BeagleBoard.org community to 
   share information about the Beagles. Spend some time 
   looking around for other helpful information.

.. _basics_onboard_flash:

Updating the Onboard Flash
===========================

Problem
--------

You want to copy the microSD card to the onboard flash.
Note, this doesn't apply to boards that
don't have onboard flash (PocketBeagle and BeagleY-AI).

Solution
--------

If you want to update the onboard flash with the contents of the microSD card, 

- Repeat the steps in :ref:`basics_install_os` to update the OS.
- Attach to an external 5 V source. *you must be powered from an external 5 V source*. The flashing process requires more current than what typically can be pulled from USB.
- Boot from the microSD card.
- Log on to the bone and edit */boot/uEnv.txt*.
- Uncomment out the last line *cmdline=init=/usr/sbin/init-beagle-flasher*.
- Save the file and reboot.
- The USR LEDs will flash back and forth for a few minutes.
- When they stop flashing, remove the SD card and reboot.
- You are now running from the newly flashed onboard flash.

.. warning:: 
   If you write the onboard flash, **be sure to power the 
   Bone from an external 5 V source**. The USB might not 
   supply enough current. 

When you boot from the microSD card, it will copy the image to the onboard flash. 
When all four *USER* LEDs turn off (in some versions, they all turn on), you can 
power down the Bone and remove the microSD card. The next time you power up, the 
Bone will boot from the onboard flash.
