.. _beagley-ai-using-gpio:

Using GPIO
#################

.. todo:: Add information about software image used for this demo.

**GPIO** stands for **General-Purpose Input/Output**. It's a set of programmable pins that you can use to connect and control various electronic components. 

You can set each pin to either **read signals (input)** from things 
like buttons and sensors or **send signals (output)** to things like LEDs and motors. This lets you interact with and control 
the physical world using code!

A great resource for understanding pin numbering can be found at `pinout.beagley.ai <https://pinout.beagley.ai/>`_ 

.. warning:: BeagleY-AI GPIOs are 3.3V tolerant, using higher voltages **WILL DAMAGE** the processor!

Pin Numbering
**********************

You will see pins referenced in several ways. While this is confusing at first, in reality, 
we can pick our favorite way and stick to it.

The two main ways of referring to GPIOs is **by their number**, so GPIO 2, 3, 4 etc. as seen in the diagram below. This corresponds
to the SoC naming convention. For broad compatibility, BeagleY-AI re-uses the Broadcom GPIO numbering scheme used by RaspberryPi. 

The second (and arguably easier) way we will use for this tutorial is to use the **actual pin header number** (shown in dark grey)

So, for the rest of the tutorial, if we refer to **hat-08-gpio** we mean the **8th pin of the GPIO header**. Which, if you referenced
the image below, can see refers to **GPIO 14 (UART TX)**

.. figure:: ../images/gpio/pinout.png
   :align: center
   :alt: BeagleY-AI pinout

   BeagleY-AI pinout


If you are curious about the "real" GPIO numbers on the Texas Instruments AM67A SoC, you can look at the board schematics. 

Required Hardware
******************

For the simple blink demo, all that is needed is an LED, a Resistor (we use 2.2K here) and 2 wires.

Similarly, a button is used for the GPIO read example, but you can also just connect that pin to 3.3V or GND with a wire 
to simulate a button press.


.. todo:: Add fritzing diagram and chapter on Pin Binding here


GPIO Write
***********

.. figure:: ../images/gpio/led-pin8.*
   :align: center
   :alt: LED connected to HAT Pin8 (GPIO14)

   LED connected to HAT Pin8 (GPIO14)

At it's most basic, we can set a GPIO using the **gpioset** command. 

- To set HAT **Pin 8** (GPIO14) to **ON**:

.. code:: console

   gpioset $(gpiofind GPIO14)=1

.. figure:: ../images/gpio/on.png
   :align: center
   :alt: GPIO ON state

   GPIO ON state

- To set HAT **Pin 8** (GPIO14) to **OFF**:

.. code:: console

   gpioset $(gpiofind GPIO14)=0

.. figure:: ../images/gpio/off.png
   :align: center
   :alt: GPIO OFF state

   GPIO OFF state

Blink an LED
**************

Let's create a script called **blinky.sh**,

- Create the file,

.. code:: console

   touch blinky.sh

- Open the file using ``nano`` editor,

.. code:: console

   nano blinky.sh

- Copy paste the code below to ``blinky.sh`` file,

.. code:: bash

   #!/bin/bash

   while :
   do
         gpioset $(gpiofind GPIO14)=1
         sleep 1
         gpioset $(gpiofind GPIO14)=0
         sleep 1
   done

- Close the editor by pressing ``Ctrl + O`` followed by ``Enter`` to save the file and then press to ``Ctrl + X`` exit

- Now execute the ``blinky.sh`` script by typing:

.. code:: console

   bash blinky.sh

.. figure:: ../images/gpio/blinky.gif
   :align: center
   :alt: LED blinking

   LED blinking

- You can exit the ``blinky.sh`` program by pressing ``CTRL + C`` on your keyboard.

Understanding the code
======================

.. callout::

   .. code-block:: bash

      #!/bin/bash

      while :
      do
         gpioset $(gpiofind GPIO14)=1 <1>
         sleep 1 <2>
         gpioset $(gpiofind GPIO14)=0 <3>
         sleep 1 <4>
      done

   .. annotations::

      The script is an infinite ``while`` loop in which we do the following:

      <1> set the HAT Pin 8 (GPIO14) as 1 (HIGH)

      <2> Wait 1 Second

      <3> set the HAT Pin 8 (GPIO14) as 0 (LOW)

      <4> Wait 1 Second

Blink an LED using Python
*************************

Using python you can blink an LED.

The ``libgpiod`` should already be installed in the default image, in case it's not installed then
install it by using the command below.

.. code:: console

   sudo apt-get install python3-libgpiod

Below is the Python code to blink an LED connected to GPIO14.

.. code-block:: console
   :caption: blinky.py

   import gpiod
   import time

   gpio14 = gpiod.find_line('GPIO14')
   gpio14.request(consumer='beagle', type=gpiod.LINE_REQ_DIR_OUT, default_val=0)

   while True:
      gpio14.set_value(1)
      time.sleep(1)
      gpio14.set_value(0)
      time.sleep(1)

To open the Python REPL, type ``python`` in the terminal like below. Copy the above code and paste it into the terminal.
After running the code, the LED connected to GPIO14 will start blinking.

.. code:: console
   
   debian@BeagleBone:~$ python
   Python 3.11.2 (main, May  2 2024, 11:59:08) [GCC 12.2.0] on linux
   Type "help", "copyright", "credits" or "license" for more information.
   >>> 

Alternatively, you can create a Python script to achieve the same effect. Create a new file named ``blinky.py`` and
open it using the ``nano`` editor with the following command, copy and paste the above code to the file.

.. code:: console

   nano blinky.py

Press ``CTRL+O`` & ``ENTER`` to save the ``blinky.py`` script and then ``CTRL+X`` to exit.

To run the ``blinky.py`` script execute the command below,

.. code:: console

   python blinky.py

After running the code you can see the LED connected to ``GPIO14`` or ``HAT Pin 08`` blinking.

Understanding the code
======================

.. callout::

   .. code-block:: bash
      
         import gpiod <1>
         import time <2>

         gpio14 = gpiod.find_line('GPIO14') <3>
         gpio14.request(consumer='beagle', type=gpiod.LINE_REQ_DIR_OUT, default_val=0) <4>

         while True: <5>
            gpio14.set_value(1) <6>
            time.sleep(1) <7>
            gpio14.set_value(0) <8>
            time.sleep(1) <9>

   .. annotations::

      <1> Importing ``gpiod`` module

      <2> Importing ``time`` module

      <3> Linking GPIO14 pin object to gpio14 variable for better accessibility

      <4> Set GPIO14 as OUTPUT pin

      <5> Create infinite ``while`` loop

      <6> Set the GPIO14 as 1 (HIGH)

      <7> Wait 1 Second

      <8> Set the GPIO14 as 0 (LOW)

      <9> Wait 1 Second

Read a Button
**************

A push button simply completes an electric circuit when pressed. Depending on wiring, it can drive a signal either "Low" (GND) or "High" (3.3V).

We will connect our Button between HAT Pin 12 (GPIO18) and Ground (GND). 

.. figure:: ../images/gpio/switch-pin12.*
   :align: center
   :alt: Button connected to HAT Pin12

   Button connected to HAT Pin12 (GPIO18)

The cool part is since we have an internal pull-up resistor, we don't need an external one!
The pull resistor guarantees that the Pin stays in a known (HIGH) state unless the button is pressed,
in which case it will go LOW.

- Reading GPIOs can be done using the ``gpioget`` command

.. code:: console

   gpioget --bias=pull-up $(gpiofind GPIO18)
   
Results in ``1`` if the Input is held ``HIGH`` or ``0`` if the Input is held ``LOW``

Let's create a script called ``button.sh`` to continuously read an input pin connected 
to a button and print out when it's pressed!

- Create the file,

.. code:: console

   touch button.sh

- Open the file using ``nano`` editor,

.. code:: console

   nano button.sh

- Copy paste the code below to ``button.sh`` file,

.. code:: bash

   #!/bin/bash

   while :
   do
      if (( $(gpioget --bias=pull-up $(gpiofind GPIO18)) == 0))
      then
         echo "Button Pressed!"
      fi
   done

- Close the editor by pressing ``Ctrl + O`` followed by ``Enter`` to save the file and then press to ``Ctrl + X`` exit

- Now execute the ``button.sh`` script by typing:

.. code:: console

   bash button.sh

- You can exit the ``button.sh`` by pressing ``Ctrl + C`` on your keyboard.

Combining the Two
**********************

.. figure:: ../images/gpio/switch-pin12-led-pin8.*
   :align: center
   :alt: Button connected to HAT Pin12 (GPIO18) & LED connected to HAT Pin8 (GPIO14)

   Button connected to HAT Pin12 (GPIO18) & LED connected to HAT Pin8 (GPIO14)

Now, logically, let's make an LED match the state of the button.

Let's create a script called **blinkyButton.sh**:

- Create the file,

.. code:: console

   touch blinkyButton.sh

- Open the file using ``nano`` editor,

.. code:: console

   nano blinkyButton.sh

- Copy paste the code below to ``blinkyButton.sh`` file,

.. code:: bash

   #!/bin/bash

   while :
   do
      if (( $(gpioget --bias=pull-up $(gpiofind GPIO18)) == 0))
      then
         gpioset $(gpiofind GPIO14)=1
      else
         gpioset $(gpiofind GPIO14)=0
      fi
   done

- Close the editor by pressing ``Ctrl + O`` followed by ``Enter`` to save the file and then press to ``Ctrl + X`` exit

- Now execute the ``blinkyButton.sh`` script by typing:

.. code:: console

   bash blinkyButton.sh

This means when we see HAT Pin 12 (GPIO18) go LOW, we know the button is pressed,
so we set HAT Pin 8 (GPIO14) (our LED) to ON, otherwise, we turn it OFF.

.. figure:: ../images/gpio/BlinkyButton.gif
   :align: center
   :alt: LED is ON when button is pressed

   LED is ON when button is pressed

- You can exit the ``blinkyButton.sh`` program by pressing ``Ctrl + C`` on your keyboard.

Understanding Internal Pull Resistors
*******************************************

Pull-up and pull-down resistors are used in digital circuits to ensure that inputs to logic settle at expected levels.

* ``Internal pull-up resistors`` connects the pin to a high voltage level (e.g., 3.3V) to ensure the pin input reads as a logic high (1) when no active device is pulling it low.

* ``Internal pull-down resistors`` connects the pin to ground (GND) to ensure the input reads as a logic low (0) when no active device is pulling it high.

These resistors prevent floating inputs and undefined states.

By default, all GPIOs on the HAT Header are configured as **Inputs with Pull-up Resistors Enabled**.

This is important for something like a button, as without it, once a button is released, it goes in an "undefined" state!

To configure Pull-ups on a per-pin basis, we can use pass the following arguments within **gpioget or gpioset**:

.. code:: console

   -B, --bias=[as-is|disable|pull-down|pull-up] (defaults to 'as-is')

The "Bias" argument has the following options:
   * **as-is** - This leaves the bias as-is... quite self explanatory
   * **disable** - This state is also known as High-Z (high impedance) where the Pin is left Floating without any bias resistor
   * **pull-down** - In this state, the pin is pulled DOWN by the internal 50KΩ resistor
   * **pull-up** - In this state, the pin is pulled UP by the internal 50KΩ resistor

For example, a command to read an input with the Bias intentionally disabled would look like this:

.. code:: bash

   gpioget --bias=disable $(gpiofind GPIO14)

Pull resistors are a foundational block of digital circuits and understanding when to (and not to) use them is important.

This article from SparkFun Electronics is a good basic primer - `Link <https://learn.sparkfun.com/tutorials/pull-up-resistors/all>`_ 

Troubleshooting
*******************

- **My script won't run!**

Make sure you gave the script execute permissions first and that you're executing it with a ``./`` before

- To make it executable:

.. code:: bash

   chmod +X scriptName.sh

- To run it:

.. code:: bash

   ./scriptName.sh


Bonus - Turn all GPIOs ON/OFF
*******************************

.. figure:: ../images/gpio/allonoff.gif
   :align: center
   :alt: All HAT GPIO toggle

   All HAT GPIO toggle

- Copy and paste this with the button on the right to turn **all pins ON**. 

.. code:: bash

   gpioset $(gpiofind GPIO14)=1 ;\ gpioset $(gpiofind GPIO15)=1 ;\ gpioset $(gpiofind GPIO17)=1 ;\ gpioset $(gpiofind GPIO18)=1 ;\ gpioset $(gpiofind GPIO27)=1 ;\ gpioset $(gpiofind GPIO22)=1 ;\ gpioset $(gpiofind GPIO23)=1 ;\ gpioset $(gpiofind GPIO24)=1 ;\ gpioset $(gpiofind GPIO10)=1 ;\ gpioset $(gpiofind GPIO9)=1 ;\ gpioset $(gpiofind GPIO25)=1 ;\ gpioset $(gpiofind GPIO11)=1 ;\ gpioset $(gpiofind GPIO8)=1 ;\ gpioset $(gpiofind GPIO7)=1 ;\ gpioset $(gpiofind GPIO1)=1 ;\ gpioset $(gpiofind GPIO6)=1 ;\ gpioset $(gpiofind GPIO12)=1 ;\ gpioset $(gpiofind GPIO13)=1 ;\ gpioset $(gpiofind GPIO19)=1 ;\ gpioset $(gpiofind GPIO16)=1 ;\ gpioset $(gpiofind GPIO26)=1 ;\ gpioset $(gpiofind GPIO21)=1

- Similarly, copy and paste this to turn **all pins OFF**. 

.. code:: bash

   gpioset $(gpiofind GPIO14)=0 ;\ gpioset $(gpiofind GPIO15)=0 ;\ gpioset $(gpiofind GPIO17)=0 ;\ gpioset $(gpiofind GPIO18)=0 ;\ gpioset $(gpiofind GPIO27)=0 ;\ gpioset $(gpiofind GPIO22)=0 ;\ gpioset $(gpiofind GPIO23)=0 ;\ gpioset $(gpiofind GPIO24)=0 ;\ gpioset $(gpiofind GPIO10)=0 ;\ gpioset $(gpiofind GPIO9)=0 ;\ gpioset $(gpiofind GPIO25)=0 ;\ gpioset $(gpiofind GPIO11)=0 ;\ gpioset $(gpiofind GPIO8)=0 ;\ gpioset $(gpiofind GPIO7)=0 ;\ gpioset $(gpiofind GPIO1)=0 ;\ gpioset $(gpiofind GPIO6)=0 ;\ gpioset $(gpiofind GPIO12)=0 ;\ gpioset $(gpiofind GPIO13)=0 ;\ gpioset $(gpiofind GPIO19)=0 ;\ gpioset $(gpiofind GPIO16)=0 ;\ gpioset $(gpiofind GPIO26)=0 ;\ gpioset $(gpiofind GPIO21)=0


Going Further
*******************

* `pinout.beagley.ai <https://pinout.beagley.ai/>`_ 
* `GPIOSet Documentation <https://manpages.debian.org/testing/gpiod/gpioset.1.en.html>`_
* `GPIOGet Documentation <https://manpages.debian.org/testing/gpiod/gpioget.1.en.html>`_
