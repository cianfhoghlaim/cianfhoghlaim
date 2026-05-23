..
    BeagleBoard projects Blink LED demo

.. _blinkLED:

Blink an LED
############

The "Hello World!" of the embedded world is to blink an LED. 
Here we'll show you how to do just that in three simple steps. 

#. Plug in the Beagle
#. Log into the Beagle
#. Blink the LED

These steps will work for any of the Beagles.

Plug in the Beagle
*******************

For this step you need to get a USB cable and attach your Beagle 
to your host computer with it.  Where you attached the cable 
depends on which Beagle you have.  Click on the tab for your board.

.. tab-set::

    .. tab-item:: Black

        .. figure:: figures/image8.jpg
            :width: 632px
            :align: center
            :alt: Tethered Configuration

            Tethered Configuration

        .. figure:: figures/image9.jpg
            :width: 451px
            :align: center
            :alt: USB Connection to the Board
        
            Mini USB Connection to the Board as seen from the bottom.

        For more details see: :ref:`beagleboneblack-connectivity`

    .. tab-item:: Blue

        .. figure:: figures/blueconnect.jpg
            :width: 451px
            :align: center
            :alt: USB Connection to the Blue

            Micro USB Connection to the Blue

    .. tab-item:: AI-64

        .. figure:: figures/usb-tethering.jpg
            :width: 400px
            :align: center 
            :alt: Tethered Configuration

            Tethered Configuration  

        .. figure:: figures/usb-c-connection.jpg
            :width: 400px
            :align: center 
            :alt: USB Connection to the Board

            USB-c Connection to the Board
            
        .. figure:: figures/usb-a-connection.jpg
            :width: 400px
            :align: center 
            :alt: USB Connection to the PC/Laptop

            USB Connection to the PC/Laptop

        .. figure:: figures/power-led.jpg
            :width: 400px
            :align: center 
            :alt: Board Power LED

            Board Power LED

        For more details see: :ref:`bbai64-quick-start`

    .. tab-item:: Play

        .. figure:: figures/tethered-connection.jpg
            :width: 1400
            :align: center
            :alt: Tethering BeaglePlay to PC

            Tethering BeaglePlay to PC

        For more details see: :ref:`beagleplay-quick-start`
            
    .. tab-item:: Pocket

        .. figure:: figures/11fig-PB-microUSBattach1.jpg
            :align: center
            :alt: Tethered Configuration

            Micro USB Connection

        For more details see: :REF:`connecting_up_pocketbeagle`
            
Once attached you will see some LEDs blinking.
Wait a bit and the blinking will settle down to a steady
heart beat.

The Beagle is now up and running, but you didn't have to 
load up Linux.  This is because all Beagles 
have built-in flash memory 
that has the Debian distribution of Linux preinstalled.

.. note:: 
    The one exception is the PocketBeagle which has no built-in 
    flash memory.  See :ref:`flash-latest-image` 
    to install an image on the Pocket

.. _intro-using-vs-code:

Using VS Code
**************

.. important:: If VS code is not installed on your board please skip this section and refer 
               to next section on how to login and run the code via command line.

Recent Beagles come with the IDE Visual Studio Code (https://code.visualstudio.com/) installed and 
running. To access it, open a web browser on your host computer and browse to: ``192.168.7.2:3000`` 
(use ``192.168.6.2:3000`` for the Mac) and you will see something like:

.. figure::  figures/vscode1.png
    :width: 740 
    :align: center

At this point you can either run the scripts via a command line within VS Code, or 
run them by clicking the ``RUN Code`` button.


Running via the command line
============================

Open a terminal window in VS Code by dropping down the ``Terminal`` menu and selecting ``New Terminal`` 
(or entering ``Ctrl+```).  The terminal window appears at the bottom of the screen as shown below.

.. figure:: figures/vscode3.png
    :width: 740 
    :align: center

You can now enter commands and see them run as shown below.

.. figure:: figures/vscode4.png
    :width: 740 
    :align: center
    
Running via the ``RUN`` button
===============================

Use the file navigator on the left to navigate to ``examples/BeagleBone/Black/blinkInternalLED.sh`` and you will see:

.. figure:: figures/vscode2.png
    :width: 740 
    :align: center

This code blinks one of the USR LEDs built into the board. Click on the ``RUN Code`` triangle on the upper right of the 
screen (see red arrow) to run the code.  (You could also enter ``Ctrl+Alt+N``) The USR3 LED should now be blinking.  

Click on the ``Stop Code Run`` (``Ctrl+Alt+M``) square to the right of the ``Run Code`` button.

Time to play!  Try changing the LED number (on line 10) from 3 to something else.  Click the ``Run Code`` 
button (no need to save the file, autosave is on by default).

Try running ``seqLEDs.py``.

Using command line
******************

To access the command line and your host is a Mac, take the ``ssh (Mac)`` tab. If you
are running Linux on your host, take the ``ssh (Linux)`` tab.  Finally take the 
``putty (Windows)`` tab for command line from Windows.

.. tab-set::

    .. tab-item:: VS Code

        Recent Beagles come with the IDE Visual Studio Code 
        (https://code.visualstudio.com/) installed and 
        running. To access it, open a web browser on 
        your host computer and browse to: ``192.168.7.2:3000`` 
        (use ``192.168.6.2:3000`` for the Mac)
        and you will see something like:

        .. figure::  figures/vscode1.png

        At this point you can either run the scripts via a command 
        line within VS Code, or run them by clicking the
        ``RUN Code`` button.


        Running via the command line

            Open a terminal window in VS Code by dropping down the 
            ``Terminal`` menu and selecting ``New Terminal`` (or entering 
            ``Ctrl+Shift+```).  The terminal window appears at the 
            bottom of the screen as shown below.

            .. figure:: figures/vscode3.png

            You can now enter commands and see them run as shown below.

            .. figure:: figures/vscode4.png

        Running via the ``RUN`` button

            Use the file navigator on the left to navigate to 
            ``examples/BeagleBone/Black/blinkInternalLED.sh`` 
            and you will see:

            .. figure:: figures/vscode2.png

            This code blinks one of the USR LEDs built into the board. 
            Click on the ``RUN Code`` triangle on the upper right of 
            the screen (see red arrow) to run the code.  (You could also enter ``Ctrl+Alt+N``) 
            The USR3 LED should now be blinking.  

            Click on the ``Stop Code Run`` (``Ctrl+Alt+M``) square to the right of the 
            ``Run Code`` button.

            
            
            Time to play!  Try changing the LED number (on line 10) from 
            3 to something else.  Click the ``Run Code`` button (no 
            need to save the file, autosave is on by default).

            Try running ``seqLEDs.py``.

    .. tab-item:: ssh (Mac)
                
        If you are running a Mac host, open a terminal widow and run 

        .. code-block:: shell-session

            host:~$ ssh debian@192.168.6.2

        Use the password ``temppwd``.
  
    .. tab-item:: ssh (Linux)

        If you are running a Linux host, open a terminal widow and run 

        .. code-block:: shell-session

            host:~$ ssh debian@192.168.7.2
        
        Use the password ``temppwd``.

    .. tab-item:: putty (Windows)

        If you are running Window you need to run an ``ssh`` client 
        to connect to the Beagle. I suggest you use ``putty``. 
        You can download it here: https://www.putty.org/. 
        Once installed, launch it and connect to your Beagle 
        by sshing to ``192.168.7.2``. 

        .. figure::  figures/putty.png

        Login with user ``debian`` 
        and password ``temppwd``.  

Blink an LED
============

Once logged in the rest is easy.  First:

.. code-block:: shell-session

    bone:~$ cd ~/examples/BeagleBone/Black
    bone:~$ ls        
    README.md              blinkInternalLED.sh  blinkLED2.py    input2.js
    analogIn.py            blinkLED.bs.js       blinkLEDold.py  seqLEDs.py
    analogInCallback.js    blinkLED.c           fadeLED.js      swipeLED.js
    analogInContinuous.py  blinkLED.js          fadeLED.py
    analogInOut.js         blinkLED.py          gpiod
    analogInSync.js        blinkLED.sh          input.js

Here you see a list of many scripts that demo simple 
input/output on the Beagle. Try one that works on the 
internal LEDs.

.. code-block:: shell-session

    bone:~$ cat blinkInternalLED.sh
    LED="3"
    
    LEDPATH='/sys/class/leds/beaglebone:green:usr'
    
    while true ; do
        echo "1" > ${LEDPATH}${LED}/brightness
        sleep 0.5
        echo "0" > ${LEDPATH}${LED}/brightness
        sleep 0.5
    done
    bone:~$ ./blinkInternalLED.sh
    ^c

:download:`blinkInternalLED.sh<code/blinkInternalLED.sh>`

Here you see a simple bash script that turns an LED 
on and off.  Enter Ctrl+c to stop the script.

Congratulations, you've blinked an LED.

Your turn
^^^^^^^^^

Now that you have an LED blinking, try blinking a different LED. 
Or, blink more than one LED at a time. Try slowing down, or speeding up 
the blink rate.

Blinking via Python
====================

Here's a script that sequences the LEDs on and off.

.. code-block:: shell-session

    bone:~$ cat seqLEDs.py
    import time
    import os

    LEDs=4
    LEDPATH='/sys/class/leds/beaglebone:green:usr'

    # Open a file for each LED
    f = []
    for i in range(LEDs):
        f.append(open(LEDPATH+str(i)+"/brightness", "w"))

    # Sequence
    while True:
        for i in range(LEDs):
            f[i].seek(0)
            f[i].write("1")     # 1 turns the LED on
            time.sleep(0.25)
        for i in range(LEDs):
            f[i].seek(0)
            f[i].write("0")     # 0 turns the LED off
            time.sleep(0.25)
    bone:~$ ./seqLEDs.py       
    ^c

:download:`seqLEDs.py<code/seqLEDs.py>`

Again, hit Ctrl+c to stop the script.

This python script is a bit more complicated that the previous bash 
script.  Note that *LEDPATH* is the same in both scripts.  They use the 
same interface to control the built-in LEDs.  The python script opens a 
file for each of the LEDs and then writes a **1** to the file to turn on 
the LED.  A **0** is writen to turn it off.  The *for* loop allows it to turn 
on (or off) all four LEDs in sequence.

Your turn
^^^^^^^^^

Try speeding up, or slowing down the sequencing by changing the *sleep* times. 
If you have programming experience, make a single LED sequence back and forth.


Blinking from Command Line
==========================

You can control the LEDs from the command line.

.. code-block:: shell-session

    bone:~$ cd /sys/class/leds
    bone:~$ ls
    beaglebone:green:usr0  beaglebone:green:usr2  mmc0::
    beaglebone:green:usr1  beaglebone:green:usr3  mmc1::

Here you see a list of LEDs. Your list may be slightly 
different depending on which Beagle you are running. 
You can blink any of them.  Let's try ``usr1``.

.. code-block:: shell-session
    
    bone:~$ cd beaglebone\:green\:usr1/
    bone:~$ ls
    brightness  device  max_brightness  power  subsystem  trigger  uevent
    bone:~$ echo 1 > brightness
    bone:~$ echo 0 > brightness

When you echo **1** into ``brightness`` the LED turns on. 
Echoing a **0** turns it off. 

Blinking other LEDs
===================

You can blink the other LEDs by changing in to thier 
directories and doing the same. Let's blink the USR0 LED.

.. code-block:: shell-session
    
    bone:~$ cd /sys/class/leds/beaglebone\:green\:usr0/
    bone:~$ echo 1 > brightness
    bone:~$ echo 0 > brightness

Did you notice that LED ``usr0`` blinks on it's own in a 
heartbeat pattern? You can set an LED trigger.  Here's 
what triggers you can set:

.. code-block:: shell-session

    bone:~$ cat trigger 
    none usb-gadget usb-host rfkill-any rfkill-none 
    kbd-scrolllock kbd-numlock kbd-capslock kbd-kanalock 
    kbd-shiftlock kbd-altgrlock kbd-ctrllock kbd-altlock 
    kbd-shiftllock kbd-shiftrlock kbd-ctrlllock kbd-ctrlrlock 
    timer oneshot disk-activity disk-read disk-write i
    de-disk mtd nand-disk [heartbeat] backlight gpio c
    pu cpu0 cpu1 cpu2 cpu3 activity default-on panic 
    netdev mmc0 mmc1 mmc2 phy0rx phy0tx phy0assoc phy0radio 
    rfkill0 gpio-0:00:link gpio-0:00:1Gbps gpio-0:00:100Mbps 
    gpio-0:00:10Mbps gpio-0:01:link gpio-0:01:10Mbps
    bone:~$ echo none > trigger

Notice ``[heartbeat]`` is in brackets.  This shows it's the 
current trigger.  The ``echo`` changes the trigger to ``none``.

Your turn 
^^^^^^^^^
Try experimenting with some of the other triggers and see if you 
can figure them out. Try changing the trigger on the other LEDs. 

.. note:: 

    The following may not work on all Beagles since it depends on which 
    version of Debian you are running.

Another way to Blink an LED
===========================

An interesting thing about Linux is there are often many ways 
to do the same thing.  For example, I can think of at least five ways to blink 
an LED.  Here's another way using the ``gpiod`` system.

First see where the LEDs are attached.

.. code-block:: shell-session

    bone:~$ gpioinfo | grep -e chip -ie  usr
    gpiochip0 - 32 lines:
    gpiochip1 - 32 lines:
        line  21: "[usr0 led]" "beaglebone:green:usr0" output active-high [used]
        line  22: "[usr1 led]" "beaglebone:green:usr1" output active-high [used]
        line  23: "[usr2 led]" "beaglebone:green:usr2" output active-high [used]
        line  24: "[usr3 led]" "beaglebone:green:usr3" output active-high [used]
    gpiochip2 - 32 lines:
    gpiochip3 - 32 lines:

Here we asked how the LEDs are attached to the General Purpose 
IO (gpio) system.  The answer is, (yours will be different for a 
different Beagle)
there are four interface chips and the LEDs are attached to 
chip 1.  You can control the gpios (and thus the LEDs) using
the ``gpioset`` command.

.. code-block:: shell-session

    bone:~$ gpioset --mode=time --sec=2 1 22=1
    bone:~$ gpioset --mode=time --sec=2 1 22=0

The first command sets chip 1, line 22 (the usr1 LED) to 1 (on) for 
2 seconds.  The second command turns it off for 2 seconds.

Your turn 
^^^^^^^^^

Try turning on and off the other LEDs. If you have programming experience, 
try modifying the earler *bash* script to use `gpiod` instead of `echo`.

.. note:: 

    The following may not work on all Beagles since it depends on which 
    version of Debian you are running.

Blinking in response to a button event
--------------------------------------

Some Beagles have a **USR** button that can be used  to control the LEDs. 
You can test the **USR** button with ``evtest`` 

.. code-block:: shell-session

    bone:~$ sudo apt install evtest
    bone:~$ evtest
    No device specified, trying to scan all of /dev/input/event*
    Not running as root, no devices may be available.
    Available devices:
    /dev/input/event0:	tps65219-pwrbutton
    /dev/input/event1:	gpio-keys
    Select the device event number [0-1]: 1

We want to use ``gpio-keys``, so enter ``1``. Press and release 
the USR button and you'll see:

.. code-block:: shell-session

    Input driver version is 1.0.1
    Input device ID: bus 0x19 vendor 0x1 product 0x1 version 0x100
    Input device name: "gpio-keys"
    Supported events:
    Event type 0 (EV_SYN)
    Event type 1 (EV_KEY)
        Event code 256 (BTN_0)
    Key repeat handling:
    Repeat type 20 (EV_REP)
        Repeat code 0 (REP_DELAY)
        Value    250
        Repeat code 1 (REP_PERIOD)
        Value     33
    Properties:
    Testing ... (interrupt to exit)
    Event: time 1692994988.305846, type 1 (EV_KEY), code 256 (BTN_0), value 1
    Event: time 1692994988.305846, -------------- SYN_REPORT ------------
    Event: time 1692994988.561786, type 1 (EV_KEY), code 256 (BTN_0), value 2
    Event: time 1692994988.561786, -------------- SYN_REPORT ------------
    Event: time 1692994988.601883, type 1 (EV_KEY), code 256 (BTN_0), value 2
    Event: time 1692994988.601883, -------------- SYN_REPORT ------------
    Event: time 1692994988.641754, type 1 (EV_KEY), code 256 (BTN_0), value 2
    Event: time 1692994988.641754, -------------- SYN_REPORT ------------
    Event: time 1692994988.641754, type 1 (EV_KEY), code 256 (BTN_0), value 0
    Event: time 1692994988.641754, -------------- SYN_REPORT ------------
    Ctrl+c 

The value **1** means the **USR** button was pressed, the **0** means it 
was released.  The value **2** means the button is being held.

The following script uses ``evtest`` to wait for the **USR** button to be 
pressed and then turns on the LED.

.. literalinclude:: code/buttonEvent.sh
    :language: Shell
    :caption: buttonEvent.sh
    :linenos:

:download:`code/buttonEvent.sh<code/buttonEvent.sh>`

Try running it and pressing the **USR** button. 

.. code-block:: shell-session

    bone:~$ ./buttonEvent.sh
    ^c

The **USR3** LED should turn on when the **USR** button is pressed.

Your turn
^^^^^^^^^
Try modifying the code to turn on a different LED.  Try blinking 2 or 3 
LEDs when the button is pressed.  Can you toggle an LED each time the 
button is pressed?

Blinking in response to a button poll
-------------------------------------

The next script polls the USR button and toggles the LED rather that waiting 
for an event.

.. literalinclude:: code/buttonLED.sh
    :language: shell
    :caption: buttonLED.sh
    :linenos:

:download:`code/buttonLED.sh<code/buttonLED.sh>`
