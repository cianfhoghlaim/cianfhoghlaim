.. _beagleconnect-technology-beagleplay-bcf:

BeaglePlay + BeagleConnect Freedom
##################################

:ref:`BeaglePlay <beagleplay-home>` and :ref:`BeagleConnect Freedom <beagleconnect-freedom-home>` are the first boards with the aim to provide seamless BeagleConnect™ Technology support over 6lowpan network which can have a range upto 1km. The support for `mikroBUS`_ add-on boards on :ref:`BeagleConnect Freedom <beagleconnect-freedom-home>` provide endless possibilties of peripherals. Let us go over some of the internal details that might be useful for developers who would like to get involved.

Architecture
************

.. note::

    This section assumes that you are familiar with terminology introduced in :ref:`beagleconnect-overview`.

:ref:`BeaglePlay <beagleplay-home>` single-board computer contains 2 processors, an AM62x running Debian Linux and a CC1352P7 co-processor. The AM62x processor acts as the :term:`AP <BeagleConnect AP>` in Greybus architecture while CC1352P7 acts as the :term:`SVC <BeagleConnect SVC>`. The sub-1 ghz networking present in CC1352P7 is used as transport. This means all greybus messages between :term:`AP <BeagleConnect AP>` and Node are routed through CC1352P7.

BeagleConnect Freedom serves as the Greybus module, running ZephyrRTOS. It has 2 `mikroBUS` ports which enables compatibility with over 1,000 mikroBUS add-on sensors, acutators, indicators and additional connectivity and storage options.

Here is a visual representation of the architecture:

.. image:: images/beagleplay_bcf_architecture.svg
   :align: center
   :alt: BeaglePlay + BeagleConnect Freedom BeagleConnet Setup


Demo
****

.. important::

    The current setup is in heavy development. In case of any problems feel free to reach out to us at `Discord <https://discordapp.com/channels/1108795636956024986/1189277127590289469>`_ or `BeagleBoard Forum <https://forum.beagleboard.org/>`_.

:ref:`greybus-host`

Here is a video of BeaglePlay + BeagleConnect Freedom in action:

.. youtube:: O5coD55JvGU
   :align: center

Components Involved
*******************

* `gb-beagleplay Linux Driver <https://elixir.bootlin.com/linux/latest/source/drivers/greybus/gb-beagleplay.c>`_: Mainline Linux Kernel since v6.7.0
* `mikroBUS Linux Driver <https://openbeagle.org/RobertCNelson/ti-linux-kernel-dev/-/tree/ti-linux-arm64-6.1.y/patches/mikrobus?ref_type=heads>`_: Out of tree
* `greybus-node-firmware <https://openbeagle.org/beagleconnect/zephyr/greybus-for-zephyr>`_: Out of tree
* `greybus-host-firmware <https://openbeagle.org/gsoc/greybus/cc1352-firmware>`_: Out of tree


Demo
****

Using Pre-built Images
=======================

The pre-built images for both BeaglePlay and BeagleConnect Freedom are available at `here <https://openbeagle.org/ayush1325/zephyr/-/jobs/23728/artifacts/download>`_.


Build Images from Source
========================

.. note::

    The following steps are for building the images from source. If you want to use pre-built images, you can skip this section.

.. todo::

    Use upstream Zephyr. The current support in Zephyr upstream has some performance problems which are being worked on. For now, we are using a custom fork based on Zephyr v3.4


Setup Zephyr
------------

.. note::

     Checkout `Zephyr Getting Started Guide <https://docs.zephyrproject.org/latest/develop/getting_started/index.html>`_ for more up to date instructions.

#. Install the required packages:

   .. code-block:: shell-session

     sudo apt install --no-install-recommends git cmake ninja-build gperf \
       ccache dfu-util device-tree-compiler wget \
       python3-dev python3-pip python3-setuptools python3-tk python3-wheel xz-utils file \
       make gcc gcc-multilib g++-multilib libsdl2-dev libmagic1 python3-venv

#. Create a new virtual environment:

   .. code-block:: shell-session

      python3 -m venv ~/zephyrproject/.venv

#. Activate the virtual environment:

   .. code-block:: shell-session

      source ~/zephyrproject/.venv/bin/activate

#. Install west:

   .. code-block:: shell-session

        pip install west

#. Get the Zephyr source code:

   .. code-block:: shell-session

      west init -m https://openbeagle.org/ayush1325/zephyr.git --mr demo-new ~/zephyrproject
      cd ~/zephyrproject
      west update

#. Export a Zephyr CMake package. This allows CMake to automatically load boilerplate code required for building Zephyr applications.

   .. code-block:: shell-session

      west zephyr-export

#. Zephyr’s scripts/requirements.txt file declares additional Python dependencies. Install them with pip.

   .. code-block:: shell-session

      pip install -r ~/zephyrproject/zephyr/scripts/requirements.txt

#. Download and verify the Zephyr SDK bundle:

   .. code-block:: shell-session

      cd ~/.local/opt
      wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.16.5-1/zephyr-sdk-0.16.5-1_linux-x86_64.tar.xz
      wget -O - https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.16.5-1/sha256.sum | shasum --check --ignore-missing

#. Extract the Zephyr SDK bundle archive:

   .. code-block:: shell-session

        tar xf zephyr-sdk-0.16.5-1_linux-x86_64.tar.xz
        rm zephyr-sdk-0.16.5-1_linux-x86_64.tar.xz

.. note::

    If trying to build on BeaglePlay, use `zephyr-sdk-0.16.5-1_linux-aarch64_minimal.tar.xz` instead of full Zephyr SDK.

#. Run the Zephyr SDK bundle setup script:

   .. code-block:: shell-session

      cd zephyr-sdk-0.16.5-1
      ./setup.sh

#. Install udev rules, which allow you to flash most Zephyr boards as a regular user:

   .. code-block:: shell-session

      sudo cp ~/zephyr-sdk-0.16.5-1/sysroots/x86_64-pokysdk-linux/usr/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d
      sudo udevadm control --reload

#. Install `cc1352-flasher <https://pypi.org/project/cc1352-flasher/>`_

   .. code-block:: shell-session

      pip install cc1352-flasher


Build and Flash BeagleConnect Freedom
-------------------------------------

#. Build Greybus for node

   .. code-block:: shell-session

      west build -b beagleconnect_freedom modules/greybus/samples/subsys/greybus/net/ -p -- -DOVERLAY_CONFIG=overlay-802154-subg.conf

#. Connect Beagleconnect Freedom and flash the firmware

   .. code-block:: shell-session

      west flash


Build and Flash BeaglePlay CC1352
---------------------------------

#. Build Greybus for host

   .. code-block:: shell-session

      west build -b beagleplay_cc1352 modules/greybus-host/ -p

#. Start BeaglePlay with bcfserial overlay. If you are using USB to UART cable to connect to BeaglePlay, you can select `BeaglePlay eMMC disable BCFSERIAL` option. Else run the following command and reboot.

   .. code-block:: shell-session

      sed -i '5d' /boot/firmware/extlinux/extlinux.conf
      sed -i '5idefault BeaglePlay eMMC disable BCFSERIAL' temp2 

#. Copy compiled image to BeaglePlay:

   .. code-block:: shell-session

      scp build/zephyr/zephyr.bin debian@beagleplay.local:~/greybus/zephyr/zephyr.bin

#. Install `cc1352-flasher <https://pypi.org/project/cc1352-flasher/>`_ on BeaglePlay

   .. code-block:: shell-session

      pip install cc1352-flasher

#. Flash the firmware

   .. code-block:: shell-session

      cc1352-flasher --play ~/greybus

#. Enable bcfserial overlay. (Skip this step if you used Uboot menu in step 2):

   .. code-block:: shell-session

      sed -i '5d' /boot/firmware/extlinux/extlinux.conf
      sed -i '5idefault BeaglePlay eMMC (default)' temp2 

#. Blacklist bcfserial Linux driver. This is required only in 5.x kernels:

   .. code-block:: shell-session

      sed -i '28s/$/ modprobe.blacklist=mikrobus/' /boot/firmware/extlinux/extlinux.conf

#. Reboot

BeaglePlay Driver
-----------------

.. note::

    This section is only required for 5.x kernels.

#. Clone the driver:

   .. code-block:: shell-session

      git clone https://git.beagleboard.org/gsoc/greybus/beagleplay-greybus-driver.git
      cd beagleplay-greybus-driver

#. Install kernel headers:

   .. code-block:: shell-session

       sudo apt install linux-headers-$(uname -r)

#. Build `gb-beagleplay` driver:

   .. code-block:: shell-session

       debian@BeaglePlay:~/beagleplay-greybus-driver$ make
       make -C /lib/modules/5.10.168-ti-arm64-r111/build M=/home/debian/beagleplay-greybus-driver modules
       make[1]: Entering directory '/usr/src/linux-headers-5.10.168-ti-arm64-r111'
         CC [M]  /home/debian/beagleplay-greybus-driver/gb-beagleplay.o
         MODPOST /home/debian/beagleplay-greybus-driver/Module.symvers
         CC [M]  /home/debian/beagleplay-greybus-driver/gb-beagleplay.mod.o
         LD [M]  /home/debian/beagleplay-greybus-driver/gb-beagleplay.ko
       make[1]: Leaving directory '/usr/src/linux-headers-5.10.168-ti-arm64-r111'

#. Load the driver:

   .. code-block:: shell-session

      sudo insmod gb-beagleplay.ko

#. Check `iio_info`. Sensors from beagleconnect freedom should show up here:

   .. code-block:: shell-session

       debian@BeaglePlay:~$ iio_info
       Library version: 0.24 (git tag: v0.24)
       Compiled with backends: local xml ip usb
       IIO context created with local backend.
       Backend version: 0.24 (git tag: v0.24)
       Backend description string: Linux BeaglePlay 5.10.168-ti-arm64-r111 #1bullseye SMP Tue Sep 26 14:22:20 UTC 2023 aarch64
       IIO context has 2 attributes:
               local,kernel: 5.10.168-ti-arm64-r111
               uri: local:
       IIO context has 2 devices:
               iio:device0: adc102s051
                       2 channels found:
                               voltage1:  (input)
                               2 channel-specific attributes found:
                                       attr  0: raw value: 4068
                                       attr  1: scale value: 0.805664062
                               voltage0:  (input)
                               2 channel-specific attributes found:
                                       attr  0: raw value: 0
                                       attr  1: scale value: 0.805664062
                       No trigger on this device
               iio:device1: hdc2010
                       3 channels found:
                               temp:  (input)
                               4 channel-specific attributes found:
                                       attr  0: offset value: -15887.515151
                                       attr  1: peak_raw value: 28928
                                       attr  2: raw value: 28990
                                       attr  3: scale value: 2.517700195
                               humidityrelative:  (input)
                               3 channel-specific attributes found:
                                       attr  0: peak_raw value: 43264
                                       attr  1: raw value: 41892
                                       attr  2: scale value: 1.525878906
                               current:  (output)
                               2 channel-specific attributes found:
                                       attr  0: heater_raw value: 0
                                       attr  1: heater_raw_available value: 0 1
                       No trigger on this device


Conclusion
**********

While BeagleConnect™ technology is still in development, we are excited to see the possibilities it brings to the table. We are continuously working on improving the technology and adding more features. Fee free to reach out to us at `Discord <https://discordapp.com/channels/1108795636956024986/1189277127590289469>`_ or `BeagleBoard Forum <https://forum.beagleboard.org/>`_.

.. _mikroBUS: https://www.mikroe.com/mikrobus
