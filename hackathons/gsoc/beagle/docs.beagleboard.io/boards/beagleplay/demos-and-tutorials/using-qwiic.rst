.. _beagleplay-qwiic:

Using QWIIC
###########

See :ref:`qwiic_stemma_grove_addons`.

A link to the appropriate I2C controller can be found at ``/dev/play/qwiic/i2c``.

OLED Display using QWIIC
=========================

Let's see a simple way to use an I2C QWIIC OLED from Sparkfun with only minor
modifications to the source code. (They will probably have this working by default in the future)

The Sparkfun Qwiic OLED Display Library Comes in 3 Parts:

- QWIIC_I2C_Py - We will need to modify this
- QWIIC-OLED-Base
- QWIIC-OLED-Display

The reason we need to modify Qwiic_I2C_Py is that by default, the library expects only one
I2C Bus to be present for something like a Raspberry Pi, but our Beagle has many!
Specifically, we want to use I2C-5 which is the bus connected to the QWIIC header.


Wiring/Connection
===================

Make the connection as shown below.

.. figure:: images/qwiic/beagleplay-qwiic-oled-connection.*
    :width: 600
    :align: center
    :alt: BeaglePlay QWIIC OLED Connection
    
    BeaglePlay QWIIC OLED Connection

You can check what bus a device is connected to by scanning it.
First lets see what buses are available.

.. code:: shell-session

    debian@BeaglePlay:~$ ls /dev/ | grep "i2c"
    i2c-0
    i2c-1
    i2c-2
    i2c-3
    i2c-5

You can now scan each bus as follows:

.. code:: shell-session

    i2cdetect -y -r 0

The ``0`` corresponds to ``i2c-0``. we can then replace ``0`` with each bus until we find the oled, 
in this case, we know we are looking for a device at address ``0x3C``.

.. code:: shell-session

    debian@BeaglePlay:~$ i2cdetect -y -r 0
        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:                         -- -- -- -- -- -- -- -- 
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    30: UU -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    50: UU -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    60: -- -- -- -- -- -- -- -- UU -- -- -- -- -- -- -- 
    70: -- -- -- -- -- -- -- --     

Note that when we see a ``UU``, this indicates that there is a device which is
currently being used by another linux process.This is most likely another I2C device that
the Beagle uses, such as the EEPROM. You can safely ignore this, but it's helpful to know
what you're looking at.

Moving on, let's see Bus 5 (Hint, I2C-5 is the QWIIC connector):

.. code:: shell-session

    debian@BeaglePlay:~$ i2cdetect -y -r 5
        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:                         -- -- -- -- -- -- -- -- 
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- -- 
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    70: -- -- -- -- -- -- -- --                         

Using Python libraries to display on OLED.
===========================================

let's install sparkfun Qwiic_I2C_Py Library.

.. code:: shell-session

    git clone https://github.com/virtualRadish/Qwiic_I2C_Py_LC

Change directory to ``Qwiic_I2C_Py_LC``.

.. code:: shell-session

    cd Qwiic_I2C_Py_LC/

Install ``setup.py``.

.. code:: shell-session

    sudo python setup.py install

Install python libraries for OLED Displays.

.. code:: shell-session

    sudo pip install sparkfun-qwiic-oled-base
    sudo pip install sparkfun-qwiic-oled-display

Let's create a file  ``HelloWorld.py`` to display some text on display.

.. code:: shell-session

    nano HelloWorld.py

Now copy paste the text below, then press CTRL+O and ENTER to save, CTRL+X to exit.

.. code:: python

    from __future__ import print_function
    import qwiic_oled_display
    import sys
    import time
    def runExample():
        #  These three lines of code are all you need to initialize the
        #  OLED and print the splash screen.
        #  Before you can start using the OLED, call begin() to init
        #  all of the pins and configure the OLED.
        print("\nSparkFun OLED Display - Hello World Example\n")
        #  Create instance with parameters for Qwiic OLED Display
        myOLED = qwiic_oled_display.QwiicOledDisplay(0x3C)
        if not myOLED.connected:
            print("The Qwiic OLED Display isn't connected to the system. Please check your connection", \
                file=sys.stderr)
            return
        myOLED.begin()

    #  clear(ALL) will clear out the OLED's graphic memory.
        myOLED.clear(myOLED.ALL) #  Clear the display's memory (gets rid of artifacts)
    #  To actually draw anything on the display, you must call the display() function.
        myOLED.display()  #  Display buffer contents
        time.sleep(1)
    #  clear(PAGE) will clear the SBC display buffer.
        myOLED.clear(myOLED.PAGE)  #  Clear the display's buffer
    #  Display buffer contents
        myOLED.display()
        time.sleep(1)
    #  Print "Hello World"
    #  ---------------------------------------------------------------------------
    #  Add text
        myOLED.print("Hello World!")
        myOLED.set_cursor(0, 10) # Set cursor to top-left
        myOLED.print("I'm BeaglePlay!")
    #  Display buffer contents
        myOLED.display()

    if __name__ == '__main__':
        try:
            runExample()
        except (KeyboardInterrupt, SystemExit) as exErr:
            print("\nEnding OLED Hello Example")
            sys.exit(0)

Now run it. After executing following command, "Hello World!" in first line and "I'm BeaglePlay!"
in second line will be printed on OLED display. 

.. code:: shell-session

    python HelloWorld.py

.. figure:: images/qwiic/beagleplay-qwiic-oled-helloworld.*
    :width: 600
    :align: center
    :alt: BeaglePlay QWIIC OLED HelloWorld.py Output

    BeaglePlay QWIIC OLED HelloWorld.py Output

Now, lets display our current IP Address. 

Shout out out to `this <https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib>`_ StackOverflow one-liner which gets our IP Address cleanly so we can
display it as a string:

.. code:: shell-session

    ipAddr = ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0]
    [1]]) + ["no IP found"])[0])

Additionally in above text we can display our current IP Address using below script.
You can create a new file then copy paste it and run.

.. code:: python

    from __future__ import print_function
    import qwiic_oled_display
    import sys
    import time
    import socket

    def runExample():

        IPAddr=(([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]

        #  These three lines of code are all you need to initialize the
        #  OLED and print the splash screen.
        #  Before you can start using the OLED, call begin() to init
        #  all of the pins and configure the OLED.
        print("\nSparkFun OLED Display - Hello World Example\n")
        #  Create instance with parameters for Qwiic OLED Display
        myOLED = qwiic_oled_display.QwiicOledDisplay(0x3C)
        if not myOLED.connected:
            print("The Qwiic OLED Display isn't connected to the system. Please check your connection", \
                file=sys.stderr)
            return
        myOLED.begin()

    #  clear(ALL) will clear out the OLED's graphic memory.
        myOLED.clear(myOLED.ALL) #  Clear the display's memory (gets rid of artifacts)
    #  To actually draw anything on the display, you must call the display() function.
        myOLED.display()  #  Display buffer contents
        time.sleep(1)
    #  clear(PAGE) will clear the SBC display buffer.
        myOLED.clear(myOLED.PAGE)  #  Clear the display's buffer
    #  Display buffer contents
        myOLED.display()
        time.sleep(1)
    #  Print "Hello World"
    #  ---------------------------------------------------------------------------
    #  Add text
        myOLED.print("Hello World!")
        myOLED.set_cursor(0, 10) # Set cursor to top-left
        myOLED.print("I'm BeaglePlay!")
        myOLED.set_cursor(0, 25) # Set cursor to top-left
        myOLED.print("My IP Is:")
        myOLED.print(IPAddr)
    #  Display buffer contents
        myOLED.display()

    if __name__ == '__main__':
        try:
            runExample()
        except (KeyboardInterrupt, SystemExit) as exErr:
            print("\nEnding OLED Hello Example")
            sys.exit(0)

You will now see current IP Address as well on OLED display.

.. figure:: images/qwiic/beagleplay-qwiic-oled-ipaddress.*
    :width: 600
    :align: center
    :alt: IP Address on QWIIC OLED Display



Credits: `Andrei Aldea, Nishka Rao, Brian Berner <https://www.hackster.io/506688/beagleplay-qwiic-oled-hello-world-ee7270>`_