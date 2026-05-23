.. _beagley-ai-quick-start:

BeagleY-AI Quick Start
######################

.. figure:: images/gpio/beagley-ai-pinout.*
    :align: center
    :alt: BeagleY-AI Pin Out Diagram

For an interactive and detailed pinout diagram, visit the `BeagleY-AI Pinout <https://pinout.beagley.ai>`_ page.

What's included in the box?
****************************

When you purchase a BeagleY-AI, you'll get the following in the box:

1. `BeagleY-AI <https://www.beagleboard.org/boards/beagley-ai>`_ with attached antenna.
2. Quick-start card

.. todo:: BeagleY-AI unboxing video

Getting started
****************

To get started your BeagleY-AI you need the following:

1. :ref:`5V @ 3A power supply <accessories-power-supplies>`
2. MicroSD card (32GB)
3. :ref:`beagley-ai-boot-media`

You may need additional accessories based on the mode of operation, you can use your BeagleY-AI in different ways.

1. :ref:`USB Tethering by directly connecting via USB type-c port <beagley-ai-usb-tethering>`
2. :ref:`Headless connection via UART debug port <beagley-ai-headless>`
3. :ref:`Standalone connection with Monitor and other peripherals attached <beagley-ai-standalone-connection>`

Easiest option is to connect the board directly to your PC or Laptop using a USB type-C to type-c cable. There is only one USB type-C port on board, if you 
choose to use a dedicated power supply for first time setup, you may choose to access the board via any other methods listed above.

Power Supply
**************

To power the board you can either connect it to a dedicated power supply like a mobile charger or a wall adapter that 
can provide 5V ≥ 3A. Checkout the :ref:`docs power supply page <accessories-power-supplies>` for power supply recommendations.

.. note:: 
    Instead of using a :ref:`power supply or power adapter <accessories-power-supplies>` if you are using a :ref:`Type-C to Type-C cable 
    <accessories-cables-usb>` to connect the board to your laptop/PC then make sure it can supply at least 1000mA.

.. _beagley-ai-boot-media:

Boot Media (Software image)
*****************************

We have two methods to prepare bootable microSD card, It is recommended to use :ref:`beagley-ai-bb-imager`.

1. :ref:`beagley-ai-bb-imager` 
2. :ref:`beagley-ai-balena-etcher`

.. _beagley-ai-bb-imager:

bb-imager
==========

Download and install `bb-imager <https://www.beagleboard.org/bb-imager>`_ for your operating system. 
Below are all the steps required to create a bootable microSD card with latest/recommended OS image for BeagleY-AI.

.. figure:: images/imager/step1-choose-device.*
    :align: center
    :alt: Click on ``CHOOSE DEVICE`` button

    Click on ``CHOOSE DEVICE`` button

.. figure:: images/imager/step2-choose-beagley-ai.*
    :align: center
    :alt: Choose ``BeagleY-AI`` board

    Choose ``BeagleY-AI`` board

.. figure:: images/imager/step3-choose-os.*
    :align: center
    :alt: Click on ``CHOOSE OS`` button

    Click on ``CHOOSE OS`` button

.. figure:: images/imager/step4-select-recommended-os.*
    :align: center
    :alt: Select ``Recommended OS``

    Select ``Recommended OS``

.. figure:: images/imager/step5-select-storage.*
    :align: center
    :alt: Click on ``CHOOSE STORAGE`` button

    Click on ``CHOOSE STORAGE`` button

.. figure:: images/imager/step6-choose-microsd-card.*
    :align: center
    :alt: Choose your microSD card

    Choose your microSD card

.. figure:: images/imager/step7-hit-next.*
    :align: center
    :alt: Click on ``Next`` button

    Click on ``Next`` button

.. figure:: images/imager/step8-edit-settings.*
    :align: center
    :alt: Click on ``EDIT SETTINGS`` button

    Click on ``EDIT SETTINGS`` button

.. figure:: images/imager/step9-settings-save.*
    :align: center
    :alt: Edit settings 

    Edit settings

.. figure:: images/imager/step9a-enable-ssh.*
    :align: center
    :alt: Under ``SERVICES`` you can enable SSH

    Under ``SERVICES`` you can enable SSH

.. figure:: images/imager/step9b-play-sound.*
    :align: center
    :alt: Under ``OPTIONS`` you can enable to play sound when flashing is finished

    Under ``OPTIONS`` you can enable to play sound when flashing is finished

.. figure:: images/imager/step10-select-yes.*
    :align: center
    :alt: Select ``YES`` to apply settings

    Select ``YES`` to apply settings

.. figure:: images/imager/step11-erase-data.*
    :align: center
    :alt: Select ``YES`` again to confirm sdCard formatting

    Select ``YES`` again to confirm sdCard formatting

.. figure:: images/imager/step12-authenticate.*
    :align: center
    :alt: Provide password to Authenticate the flashing process

    Provide password to Authenticate the flashing process

.. figure:: images/imager/step13-download-started.*
    :align: center
    :alt: Download image else automatically open cached image

    Download image else automatically open cached image

.. figure:: images/imager/step14-writing.*
    :align: center
    :alt: Writing data to microSD card

    Writing data to microSD card

.. figure:: images/imager/step15-verifying.*
    :align: center
    :alt: Verifying flashed microSD card

    Verifying flashed microSD card

.. figure:: images/imager/step16-sdcard-ready.*
    :align: center
    :alt: microSD card is ready

    microSD card is ready

.. _beagley-ai-balena-etcher:

Balena Etcher
==============

Download and install `Balena Etcher <https://etcher.balena.io/>`_ and then download the boot media from
`https://www.beagleboard.org/distros/beagley-ai-debian-12-5-2024-06-19-xfce <https://www.beagleboard.org/distros/beagley-ai-debian-12-5-2024-06-19-xfce>`_. 
Flash it on a microSD card using `Balena Etcher <https://etcher.balena.io/>`_ following the steps below:

1. Select downloaded boot media
2. Select microSD card 
3. Flash!

.. tip:: For more detailed steps checkout the :ref:`beagleboard-getting-started` under support section of the documentation.

.. figure:: images/balena-etcher.*
    :align: center
    :alt: Flashing BeagleY-AI boot image (software image) to microSD card

    Flashing BeagleY-AI boot image (software image) to microSD card

Once the microSD card is flashed you should see ``BOOT`` and ``rootfs`` mounted on your system as shown in image below,

.. figure:: images/disk.*
    :align: center
    :alt: Flashed microSD card mounted partitions

    Flashed microSD card mounted partitions

Under ``BOOT`` partition open ``sysconf.txt`` to edit login ``username`` and ``password``.

.. figure:: images/sysconf.*
    :align: center
    :alt: sysconf file under BOOT partition

    sysconf file under BOOT partition

In ``sysconf.txt`` file you have to edit the two lines highlighted below. 

.. callout::

    .. code-block:: text
        :linenos:
        :lineno-start: 29
        :emphasize-lines: 2,5

        # user_name - Set a user name for the user (1000)
        #user_name=beagle <1>

        # user_password - Set a password for user (1000)
        #user_password=FooBar <2>

    .. annotations::

        <1> If ``boris`` is your username, update ``#user_name=beagle`` to ``user_name=boris``

        <2> If ``bash`` is your password, update ``#user_password=FooBar`` to ``user_password=bash``

.. important::
    
    1. Make sure to remove ``#`` from ``#user_name=`` and ``#user_password=`` else the lines will be interpreted as a comment and your username & password will not be updated.
    2. If you do not change your username and passord here then you will not see any output on your HDMI monitor when you do a :ref:`beagley-ai-standalone-connection` setup.


Once username and password are updated, you can insert the microSD card into 
your BeagleY-AI as shown in the image below:

.. figure:: images/beagley-ai-micro-sd-card.*
    :align: center
    :alt: Insert microSD card in BeagleY-AI

    Insert microSD card in BeagleY-AI

.. _beagley-ai-usb-tethering:

USB Tethering
**************

.. note:: 
    If you are using the board with a fan or running a computationally intensive 
    task you should always power the board with a dedicated power supply that can supply 5V ≥ 3A (15W+). 

    As per USB standards these are the current at 5V that each downstream USB port type can (max) supply:

    - USB Type-A 3.x port - 900mA (4.5W)
    - USB Type-C 1.2 port - 1500mA (7.5W) to 3000mA (15W)

    Thus it's recommended to use type-C to type-C cable.

To initially test your board, you can connect the board directly to your computer using a ``type-C to type-C`` cable shown in the image below.

.. figure:: images/beagley-ai-tethered-connection.*
    :align: center
    :alt: BeagleY-AI tethered connection

    BeagleY-AI tethered connection

SSH connection
===============

After connecting, you should see the power LED glow, and soon just like with other Beagles, BeagleY-AI will create a virtual wired connection on your computer. 
To access the board, open up a terminal (`Linux <https://www.wikihow.com/Open-a-Terminal-Window-in-Ubuntu>`_/`Mac <https://www.wikihow.com/Open-a-Terminal-Window-in-Mac>`_) 
or command prompt (`Windows <https://www.wikihow.com/Open-the-Command-Prompt-in-Windows>`_) and use the SSH command as shown below.

.. code:: shell
    
    ssh debian@192.168.7.2

.. important:: Here ``debian`` is the default username, make sure to replace ``debian`` with the ``username`` you selected during :ref:`beagley-ai-boot-media` preparation step.

.. tip:: If you are not able to find your beagle at ``192.168.7.2``, checkout :ref:`start-browse-to-beagle` to resolve your connection issue.

.. important:: If you have not updated your default username and password during :ref:`beagley-ai-boot-media`, you must update the default password at this step to something safer.

.. figure:: images/ssh-connection.*
    :align: center 
    :alt: BeagleY-AI SSH connection

    BeagleY-AI SSH connection

.. _beagley-ai-uart-connection:

UART connection
================

Your BeagleY-AI board creates a UART connection (No additional hardware required) when tethered to a Laptop/PC which you can access using ``Putty`` of ``tio``. 
On a linux machine it may come up as ``dev/ttyACM*``, it will be different for Mac and Windows operating systems. To find serial port for your system you can checkout 
`this guide <https://www.mathworks.com/help/matlab/supportpkg/find-arduino-port-on-windows-mac-and-linux.html;jsessionid=c2d3127cd10411c66f33468cbd5b>`_.

.. figure:: images/uart/putty.*
    :align: center
    :alt: Putty serial connection

    Putty serial connection

- If you are on linux, try ``tio`` with default setting using command below,

.. code:: console

    tio /dev/ttyACM0

With this you have the access to BeagleY-AI terminal. Now, you can connect your board to :ref:`WiFi <beagley-ai-connecting-wifi>`, 
try out all the :ref:`cool demos <beagley-ai-demos>` and explore all the other ways to access your BeagleY-AI listed below.

- :ref:`beagley-ai-connecting-wifi`
- :ref:`beagley-ai-demos`

.. _beagley-ai-headless:

Headless connection
===================

If you want to run your BeagleY-AI in headless mode, you need `Raspberry Pi Debug Probe <https://www.raspberrypi.com/documentation/microcontrollers/debug-probe.html>`_ 
or similar serial (USB to UART) adapter. Connect your UART debug probe to BeagleY-AI as shown in the image below. After making the connection you can use command 
line utility like ``tio`` on Linux or Putty on any operating system. Check :ref:`beagley-ai-uart-connection` for more information.

.. figure:: images/uart/rpi-debug-probe-connection.*
    :align: center
    :alt: Connecting Raspberry Pi debug probe to BeagleY-AI

    Connecting Raspberry Pi debug probe to BeagleY-AI

.. _beagley-ai-standalone-connection:

Standalone connection
=====================

.. important:: 
    Make sure to update your ``username`` and ``password`` during 
    :ref:`beagley-ai-boot-media` preparation step else you'll not see any output on you HDMI monitor.

To setup your BeagleY-AI for standalone usage, you need the following additional accessories,

1. HDMI monitor
2. micro HDMI to full-size HDMI cable
3. Wireless keyboard & mice combo
4. Ethernet cable (Optional)

Make sure you have the microSD card with boot media (software image) inserted in to the BeagleY-AI. Now connect,

1. microHDMI to BeagleY-AI and full size HDMI to monitor
2. keyboard and mice combo to one of the four USB port of BeagleY-AI
3. Power supply to USB type-c connector of BeagleY-AI

The connection diagram below provides a clear representation of all the connections,

.. figure:: images/standalone.*
    :align: center
    :alt: BeagleY-AI standalone connection

    BeagleY-AI standalone connection

If everything is connected properly you should see four penguins on your monitor.

.. figure:: images/boot-penguins.*
    :align: center
    :alt: BeagleY-AI boot penguins

    BeagleY-AI boot penguins

When prompted, login using the credentials you updated during :ref:`beagley-ai-boot-media` preparation step.

.. Important:: You can not update login credentials at this step, you must update them during boot media (software image) micrSD card flashing or USB tethering step!

.. figure:: images/login.*
    :align: center
    :alt: BeagleY-AI XFCE desktop login

    BeagleY-AI XFCE desktop login

Once logged in you should see the splash screen shown in the image below:

.. figure:: images/screen-saver.*
    :align: center
    :alt: BeagleY-AI XFCE home screen

    BeagleY-AI XFCE home screen

Test network connection by running ``ping 8.8.8.8``

.. figure:: images/ping-test.*
    :align: center
    :alt: BeagleY-AI network ping test

    BeagleY-AI network ping test

Explore and build with your new BeagleY-AI board!

.. figure:: images/htop.*
    :align: center
    :alt: BeagleY-AI running htop

    BeagleY-AI running htop

.. _beagley-ai-connecting-wifi:

Connecting to WiFi
**********************

The onboard ``BM3301`` can connect to any 2.5GHz wifi access point. 
We have two options to connect to WiFi,

1. :ref:`beagley-ai-nmtui`
2. :ref:`beagley-ai-iwctl`

.. _beagley-ai-nmtui:

nmtui
======

- Enable ``NetworkManager``

.. code:: console

    sudo systemctl enable NetworkManager

- Start ``NetworkManager``

.. code:: console

    sudo systemctl start NetworkManager

- Start ``nmtui`` application

.. code:: console

    sudo nmtui

- To navigate, use the ``arrow keys`` or press ``Tab`` to step forwards and press ``Shift+Tab`` to step back through the options. Press ``Enter`` to select an option. The ``Space bar`` toggles the status of a check box.
- You should see a screen as shown below, here you have to press ``Enter`` on ``Acticate a connection`` option to `activate wired and wireless connection options <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/networking_guide/sec-configuring_ip_networking_with_nmtui>`_.

.. figure:: images/wifi/nmtui.*
    :align: center
    :alt: NetworkManager TUI

    NetworkManager TUI

There under ``WiFi`` section press ``Enter`` on desired access point and provide password to connect. When successfully connected press ``Esc`` to get out of the ``nmtui`` application window.

.. _beagley-ai-iwctl:

iwctl
======

Once board is fully booted and you have access to the shell, follow the commands below to connect to any WiFi access point,

- To list the wireless devices attached, (you should see wlan0 listed)

.. code:: shell

    iwctl device list

- Scan WiFi using,

.. code:: shell

    iwctl station wlan0 scan

- Get networks using, 

.. code:: shell

    iwctl station wlan0 get-networks

- Connect to your wifi network using, 

.. code::

    iwctl --passphrase "<wifi-pass>" station wlan0 connect "<wifi-name>"

- Check wlan0 status with, 

.. code::

    iwctl station wlan0 show

- To list the networks with connected WiFi marked you can again use, 

.. code::

    iwctl station wlan0 get-networks

- Test connection with ping command,

.. code::
    
    ping 8.8.8.8

Attach cooling fan
*******************

To attached the Raspberry Pi cooling fan to BeagleY-AI you have to follow these steps,

1. Clean the surface of BeagleY-AI with a microfiber cloth or electronics safe cleaning brush.
2. Gently pull the pre-cut (blue) thermal pads from cooling fan surface and transfer them to the most heating parts of BegleY-AI like CPU and RAM.
3. Connect the fan cable, then carefully place the flat part of cooling fan on BeagleY-AI. Now, gently apply force on spring loaded push pins to securely attach the cooling fan.

.. figure:: images/fan/fan-connection.*
    :align: center
    :alt: Attaching cooling fan to BeagleY-AI

    Attaching cooling fan to BeagleY-AI

Demos and Tutorials
*******************

* :ref:`beagley-ai-using-gpio`
* :ref:`beagley-ai-using-rtc`
* :ref:`beagley-ai-using-pwm`
* :ref:`beagley-ai-using-i2c-adc`
* :ref:`beagley-ai-expansion-nvme`
* :ref:`beagley-ai-object-detection-tutorial`
* :ref:`beagley-ai-using-i2c-oled-display`
* :ref:`beagley-ai-using-imx219-csi-cameras`
* :ref:`beagley-ai-pca9685-motor-drivers`
* :ref:`beagley-ai-arducam-imx219-v3link-dual-camera-kit`
