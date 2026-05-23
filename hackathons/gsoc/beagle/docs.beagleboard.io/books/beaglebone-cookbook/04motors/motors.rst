.. _beaglebone-cookbook-motors:

Motors
########

.. |kohm| replace:: kΩ

.. |ohm| replace:: Ω

.. |deg| replace:: °

.. todo
    Figure out degrees

One of the many fun things about embedded computers is that you can move physical things with motors.
But there are so many different kinds of motors (``servo``, ``stepper``, ``DC``), so how do you select the right one?

The type of motor you use depends on the type of motion you want:

- R/C or hobby servo motor
    Can be quickly positioned at various absolute angles, but some don't spin. In fact, many can turn only about 180{deg}.
- Stepper motor
    Spins and can also rotate in precise relative angles, such as turning 45°. Stepper motors come in two types: ``bipolar`` (which has four wires) and ``unipolar`` (which has five or six wires).
- DC motor
    Spins either clockwise or counter-clockwise and can have the greatest speed of the three. But a DC motor can't easily be made to turn to a given angle.
        
When you know which type of motor to use, interfacing is easy. This chapter shows how to interface with each of these motors.

.. note:: 
    Motors come in many sizes and types. This chapter presents some of the more popular 
    types and shows how they can interface easily to the Bone. If you need to turn on and 
    off a 120 V motor, consider using something like the PowerSwitch presented in :ref:`displays_powerSwitch`.

.. note:: 
    The Bone has built-in 3.3 V and 5 V supplies, which can supply enough current to drive 
    some small motors. Many motors, however, draw enough current that an external power 
    supply is needed. Therefore, an external 5 V power supply is listed as optional in many of the recipes.

.. note:: 
    All the examples in the book assume you have cloned the Cookbook repository on 
    git.beagleboard.org. Go here :ref:`basics_repo` for instructions.

.. _motors_servo:

Controlling a Servo Motor
==========================

Problem
--------

You want to use BeagleBone to control the absolute position of a servo motor.

Solution
--------

We'll use the pulse width modulation (PWM) 
hardware of the Bone to control a servo motor.

To make the recipe, you will need:

* Servo motor.
* Breadboard and jumper wires.
* 1 |kohm| resistor (optional)
* 5 V power supply (optional)

The 1 |kohm| resistor isn't required, but it provides some protection to the general-purpose 
input/output (GPIO) pin in case the servo fails and draws a large current. 

Wire up your servo, as shown in :ref:`motors_servoMotor`.  

.. note:: 
    There is no standard for how servo motor wires are colored. One of my servos is wired 
    like :ref:`motors_servoMotor` red is 3.3 V, black is ground, and yellow is the control line. 
    I have another servo that has red as 3.3 V and ground is brown, with the control line being orange. 
    Generally, though, the 3.3 V is in the middle. Check the datasheet for your servo before wiring.

.. _motors_servoMotor:

.. figure:: figures/servoMotor_bb.png
    :align: center
    :alt: Servo Motor

    Driving a servo motor with the 3.3 V power supply

The code for controlling the servo motor is in ``servoMotor.py``, shown 
in :ref:`py_servoMotor_code`. 

.. tab-set::

    .. tab-item:: Python

        .. _py_servoMotor_code:

        .. literalinclude:: ../code/04motors/servoMotor.py
            :caption: Code for driving a servo motor (servoMotor.py)
            :language: Python
            :linenos:

        :download:`servoMotor.py <../code/04motors/servoMotor.py>`

    .. tab-item:: JavaScript

        .. _motors_servoMotor_code:

        .. literalinclude:: ../code/04motors/servoMotor.js
            :caption: Code for driving a servo motor (servoMotor.js)
            :language: JavaScript
            :linenos:

        :download:`servoMotor.js <../code/04motors/servoMotor.js>`

You need to configure the pin for PWM.

.. tab-set::

    .. tab-item:: BeagleBone

        .. code-block:: bash

            bone$ cd ~/beaglebone-cookbook-code/04motors
            bone$ config-pin P9_16 pwm
            bone$ ./servoMotor.py
    
    .. tab-item:: BeagleY-AI

        Configuring the PWM on the BeagleY-AI takes a little more effort than on the Bone.
        First select which PWM you want to use. https://pinout.beagleboard.io/pinout/pwm
        shows you have many to choose from. 

        .. figure:: figures/pwm.png
            :align: center
            :alt: BeagleY-AI PWMs

            BeagleY-AI PWMs

        Let's use **PWM0** on **GPIO12**.  Note this is Hat pin 32 as shown in the figure (**hat-32**).
        The instructions at :ref:`beagley-ai-using-pwm` give details on how to configure the PWM pin. A shorter version is given here.

        To enable any of the PWM Pins, we have to modify the file: ``/boot/firmware/extlinux/extlinux.conf``. We can check the available list of Device Tree Overlays using the command:

        .. code:: console

            debian@BeagleBone:~$ ls /boot/firmware/overlays/ | grep "beagley-ai-pwm"
            k3-am67a-beagley-ai-pwm-ecap0-gpio12.dtbo
            k3-am67a-beagley-ai-pwm-ecap1-gpio16.dtbo
            k3-am67a-beagley-ai-pwm-ecap1-gpio21.dtbo
            ...

        Add the line shown below to ``/boot/firmware/extlinux/extlinux.conf`` to load the gpio12 pwm device tree overlay:

        .. code:: bash

            fdtoverlays /overlays/k3-am67a-beagley-ai-pwm-epwm0-ecap0-gpio12.dtbo

        Your ``/boot/firmware/extlinux/extlinux.conf`` file should look something like:

        .. code:: bash

            label microSD (default)
                kernel /Image
                append console=ttyS2,115200n8 root=/dev/mmcblk1p3 ro rootfstype=ext4 resume=/dev/mmcblk1p2 rootwait net.ifnames=0 quiet
                fdtdir /
                fdt /ti/k3-am67a-beagley-ai.dtb
                fdtoverlays /overlays/k3-am67a-beagley-ai-pwm-ecap0-gpio12.dtbo
                initrd /initrd.img

        Now reboot you BeagleY-AI to load the overlay:

        .. code:: console

            beagle$ sudo reboot

        To configure HAT pin32 (GPIO12) PWM symlink pin using ``beagle-pwm-export`` execute the command below,

        .. code:: console

            beagle$ sudo beagle-pwm-export --pin hat-32

        We've changed the PWM pin that's being used so we need to modfiy ``servoMotor.py``.  
        Around line 16 you will see:

            PWMPATH='/dev/bone/pwm/'+pwm+'/'+channel

        Change it to:

            PWMPATH='/dev/hat/pwm/GPIO12'

        Now run your code:

            beagle$ ./servoMotor.py

Running the code causes the motor to move back and forth, progressing to successive  
positions between the two extremes.  You will need to press ^C (Ctrl-C) to stop the script.

Controlling a Servo with an Rotary Encoder
==========================================

Problem
--------

You have a rotary encoder from from chapter 2 rotary encoder example that you want to use to control a servo motor.

Solution
---------

Combine the code from ``rotaryEncoder.js`` and ``servoMotor.js``.


.. code-block:: bash

    bone$ config-pin P9_16 pwm
    bone$ config-pin P8_11 eqep
    bone$ config-pin P8_12 eqep
    bone$ ./servoEncoder.py

.. _py_servoEncoder_code:

.. literalinclude:: ../code/04motors/servoEncoder.py
   :language: py
   :caption: Code for driving a servo motor with a rotary encorder(servoEncoder.py)
   :linenos:

:download:`servoEncoder.py <../code/04motors/servoEncoder.py>`

.. _motors_dcSpeed:

Controlling the Speed of a DC Motor
===================================

Problem
--------

You have a DC motor (or a solenoid) and want a simple way to control its speed, but not the direction.

Solution
---------

It would be nice if you could just wire the DC motor to BeagleBone Black and have it work, 
but it won't.  Most motors require more current than the GPIO ports on the Bone can supply. 
Our solution is to use a transistor to control the current to the bone. 

Here we configure the encoder to returns value between 0 and 180 inclusive. This value is then 
mapped to a value between *min* (0.6 ms) and *max* (2.5 ms).  This number is converted from 
milliseconds and nanoseconds (time 1000000) and sent to the servo motor via the pwm.


Here's what you will need:

* 3 V to 5 V DC motor
* Breadboard and jumper wires.
* 1 |kohm| resistor.
* Transistor 2N3904.
* Diode 1N4001.
* Power supply for the motor (optional)

If you are using a larger motor (more current), 
you will need to use a larger transistor.

Wire your breadboard as shown in :ref:`motors_dcMotor_fig`.

.. _motors_dcMotor_fig:

.. figure:: figures/dcMotor_bb.png
    :align: center
    :alt: DC Motor

    Wiring a DC motor to spin one direction

Use the code in :ref:`py_dcMotor_code` to run the motor.

.. tab-set::

    .. tab-item:: Python

        .. _py_dcMotor_code:

        .. literalinclude:: ../code/04motors/dcMotor.py
                :caption: Driving a DC motor in one direction (dcMotor.py)
                :language: Python
                :linenos:

        :download:`dcMotor.py <../code/04motors/dcMotor.py>`

    .. tab-item:: JavaScript

        .. _motors_dcMotor_code:

        .. literalinclude:: ../code/04motors/dcMotor.js
            :caption: Driving a DC motor in one direction (dcMotor.js)
            :language: JavaScript
            :linenos:

        :download:`dcMotor.js <../code/04motors/dcMotor.js>`

See Also
=========

How do you change the direction of the motor? See :ref:`motors_dcDirection`.

.. _motors_dcDirection:

Controlling the Speed and Direction of a DC Motor
==================================================

Problem
--------

You would like your DC motor to go forward and backward.

Solution
---------

Use an H-bridge to switch the terminals on the motor so that it will run both backward 
and forward. We'll use the ``L293D`` a common, single-chip H-bridge.

Here's what you will need:

* 3 V to 5 V motor.
* Breadboard and jumper wires.
* L293D H-Bridge IC.
* Power supply for the motor (optional)

Lay out your breadboard as shown in :ref:`motors_h-bridge_fig`. Ensure that the L293D is positioned correctly. 
There is a notch on one end that should be pointed up.

.. _motors_h-bridge_fig:

.. figure:: figures/h-bridgeMotor_bb.png
    :align: center
    :alt: H-bridge Motor

    Driving a DC motor with an H-bridge

The code in :ref:`motors_h-bridge_code` (``h-bridgeMotor.js``) looks much like the code for driving the DC 
motor with a transistor (:ref:`motors_dcMotor_code`). The additional code specifies which direction to spin the motor.

.. _motors_h-bridge_code:

.. literalinclude:: ../code/04motors/h-bridgeMotor.js
   :language: js
   :caption: Code for driving a DC motor with an H-bridge (h-bridgeMotor.js)
   :linenos:

:download:`h-bridgeMotor.js <../code/04motors/h-bridgeMotor.js>`

Driving a Bipolar Stepper Motor
===============================

Problem
--------

You want to drive a stepper motor that has four wires.

Solution
---------

Use an L293D H-bridge. The bipolar stepper motor requires 
us to reverse the coils, so we need to use an H-bridge.

Here's what you will need:

* Breadboard and jumper wires.
* 3 V to 5 V bipolar stepper motor.
* L293D H-Bridge IC.

Wire as shown in :ref:`motors_bipolar_fig`.

.. _motors_bipolar_fig:

.. figure:: figures/bipolarStepperMotor_bb.png
    :align: center
    :alt: Bipolar Stepper Motor

    Bipolar stepper motor wiring

Use the code in :ref:`motors_stepperMotor_code_py` to drive the motor.

.. _motors_stepperMotor_code_py:

.. literalinclude:: ../code/04motors/bipolarStepperMotor.py
   :language: py
   :caption: Driving a bipolar stepper motor (bipolarStepperMotor.py)
   :linenos:

:download:`bipolarStepperMotor.py <../code/04motors/bipolarStepperMotor.py>`

When you run the code, the stepper motor will rotate back and forth.


Driving a Unipolar Stepper Motor
=================================

Problem
--------

You want to drive a stepper motor that has five or six wires.

Solution
---------

If your stepper motor has five or six wires, it's a ``unipolar`` stepper and 
is wired differently than the bipolar. Here, we'll use 
a ``ULN2003 Darlington Transistor Array IC`` to drive the motor.

Here's what you will need:

* Breadboard and jumper wires.
* 3 V to 5 V unipolar stepper motor.
* ULN2003 Darlington Transistor Array IC.

Wire, as shown in :ref:`motors_unipolar_fig`. 

.. note:: 

    The IC in :ref:`motors_unipolar_fig` is illustrated 
    upside down from the way it is usually displayed. 

    That is, the notch for pin 1 is on the bottom. This made drawing the diagram much cleaner.

    Also, notice the ``banded`` wire running the *P9_7* (5 V) to the UL2003A. 
    The stepper motor I'm using runs better at 5 V, so I'm using the Bone's 5 V power supply. 
    The signal coming from the GPIO pins is 3.3 V, but the U2003A will step them up to 5 V to drive 
    the motor.

.. _motors_unipolar_fig:

.. figure:: figures/unipolarStepperMotor_bb.png
    :align: center
    :alt: Unipolar Stepper Motor

    Unipolar stepper motor wiring

The code for driving the motor is in ``unipolarStepperMotor.js`` however, it is 
almost identical to the bipolar stepper code (:ref:`motors_stepperMotor_code_py`), 
so :ref:`motors_unistepperMotor_code` shows only the lines that you need to change.

.. _motors_unistepperMotor_js_code:

.. literalinclude:: ../code/04motors/unipolarStepperMotor.py.diff
   :caption: Changes to bipolar code to drive a unipolar stepper motor (unipolarStepperMotor.py.diff)
   :linenos:

:download:`unipolarStepperMotor.py.diff <../code/04motors/unipolarStepperMotor.py.diff>`

.. _motors_unistepperMotor_code:

.. literalinclude:: ../code/04motors/unipolarStepperMotor.js.diff
   :caption: Changes to bipolar code to drive a unipolar stepper motor (unipolarStepperMotor.js.diff)
   :linenos:

:download:`unipolarStepperMotor.js.diff <../code/04motors/unipolarStepperMotor.js.diff>`


The code in this example makes the following changes:

* The *states* are different. Here, we have two pins high at a time.
* The time between steps (*ms*) is shorter, and the number of steps per direction (*max*) is bigger. The unipolar stepper I'm using has many more steps per rotation, so I need more steps to make it go around.
