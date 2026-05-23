.. _beagley-ai-using-pwm:

Pulse Width Modulation (PWM)
#############################

.. todo:: Add further testing steps, results, and images..

What is it
************

``PWM`` or ``Pulse Width Modulation``, is a technique used to control the amount of power delivered to an electronic device by breaking up the power signal into discrete ON and OFF periods. 
The amount of time the signal spends ON during each cycle determines the output power level (brightness of the LED).

.. image:: ../images/gpio/pwm.jpg
   :width: 50%
   :align: center

Configuring PWM overlay
************************

To enable any of the PWM Pins, we have to modify the following file: ``/boot/firmware/extlinux/extlinux.conf``. We can check the available list of Device Tree Overlays using command below,

.. code:: console

   ls /boot/firmware/overlays/ | grep "beagley-ai-pwm"

When executed the above command should give output show below,

.. code:: console

   debian@BeagleBone:~$ ls /boot/firmware/overlays/ | grep "beagley-ai-pwm"
   k3-am67a-beagley-ai-pwm-ecap0-gpio12.dtbo
   k3-am67a-beagley-ai-pwm-ecap1-gpio16.dtbo
   k3-am67a-beagley-ai-pwm-ecap1-gpio21.dtbo
   k3-am67a-beagley-ai-pwm-ecap2-gpio17.dtbo
   k3-am67a-beagley-ai-pwm-ecap2-gpio18.dtbo
   k3-am67a-beagley-ai-pwm-epwm0-gpio12.dtbo
   k3-am67a-beagley-ai-pwm-epwm0-gpio14.dtbo
   k3-am67a-beagley-ai-pwm-epwm0-gpio15.dtbo
   k3-am67a-beagley-ai-pwm-epwm0-gpio5.dtbo
   k3-am67a-beagley-ai-pwm-epwm1-gpio13.dtbo
   k3-am67a-beagley-ai-pwm-epwm1-gpio20.dtbo
   k3-am67a-beagley-ai-pwm-epwm1-gpio21.dtbo
   k3-am67a-beagley-ai-pwm-epwm1-gpio6.dtbo

Using hat-08 (GPIO14) as pwm
=============================

Add the line shown below to ``/boot/firmware/extlinux/extlinux.conf`` file to load the gpio14 pwm device tree overlay:

.. code:: bash

   fdtoverlays /overlays/k3-am67a-beagley-ai-pwm-epwm0-gpio14.dtbo

Your ``/boot/firmware/extlinux/extlinux.conf`` file should look something like this:

.. code:: bash

   label microSD (default)
      kernel /Image
      append console=ttyS2,115200n8 root=/dev/mmcblk1p3 ro rootfstype=ext4 resume=/dev/mmcblk1p2 rootwait net.ifnames=0 quiet
      fdtdir /
      fdt /ti/k3-am67a-beagley-ai.dtb
      fdtoverlays /overlays/k3-am67a-beagley-ai-pwm-epwm0-gpio14.dtbo
      initrd /initrd.img

Now reboot you BeagleY-AI to load the overlay,

.. code:: console

   sudo reboot

How do we do it
*****************

To configure HAT pin8 (GPIO14) PWM symlink pin using ``beagle-pwm-export`` execute the command below,

.. code:: console

    sudo beagle-pwm-export --pin hat-08

Let's create a script called ``fade.sh`` that cycles through LED brightness on HAT pin8 by changing PWM duty cycle.

.. code:: console

    touch fade.sh

Now open the file with nano editor,

.. code:: console

    nano fade.sh

In the editor copy paste the script content below,

.. code:: bash

    #!/bin/bash

    PWMPIN="/dev/hat/pwm/GPIO14"


    echo 1000 > $PWMPIN/period
    echo 0 > $PWMPIN/duty_cycle
    echo 0 > $PWMPIN/enable
    sleep 1

    for i in {1..500};
    do
	    echo $i > $PWMPIN/duty_cycle
	    echo 1 > $PWMPIN/enable
	    echo $i
	    sleep 0.0005
    done

    for i in {500..1};
    do
        echo $i > $PWMPIN/duty_cycle
        echo 1 > $PWMPIN/enable
        echo $i
        sleep 0.0005
    done
    
- Close the editor by pressing ``Ctrl + O`` followed by ``Enter`` to save the file and then press to ``Ctrl + X`` exit

- Now execute the ``fade.sh`` script by typing:

.. code:: console

   bash fade.sh

.. figure:: ../images/gpio/pwm.gif
   :align: center
   :alt: LED PWM fade demo

   LED PWM fade demo

- You can exit the ``fade.sh`` program by pressing ``Ctrl + C`` on your keyboard.

.. todo:: Add section about driving Servo Motors at 50KHz

Troubleshooting
*******************

.. todo:: Fill out empty section

Going Further
*******************

.. todo:: Fill out empty section
