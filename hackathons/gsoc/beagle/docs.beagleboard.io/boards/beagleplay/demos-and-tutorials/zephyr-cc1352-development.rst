.. _beagleplay-zephyr-development:

Wireless MCU Zephyr Development
###############################

BeaglePlay includes a `Texas Instruments CC1352P7 wireless microcontroller (MCU) <https://www.ti.com/product/CC1352P7>`_
that can be programmed using the `Linux Foundation Zephyr RTOS <https://www.zephyrproject.org/>`_.

Developing directly in Zephyr will not be ultimately required for end-users 
who won't touch the firmware running on the CC1352 on BeaglePlay™ and will instead
use the provided wireless functionality. However, it is important for early 
adopters as well as people looking to extend the functionality of the open 
source design. If you are one of those people, this is a good place to get 
started.

Further, BeaglePlay is a reasonable development platform for creating Zephyr-based
applications for :ref:`beagleconnect-freedom-home`. The same Zephyr development
environment setup here is also described for targeting applications on that board.

Install the latest software image for BeaglePlay
*************************************************

.. note::

    These instructions should be generic for BeaglePlay and other boards and only the
    specifics of which image was used to test these instructions need be included
    here moving forward and the detailed instructions can be referenced elsewhere.

You may want to download and install the latest Debian Linux operating system
image for BeaglePlay.

.. note::

    These instructions were validated with the BeagleBoard.org Debian image
    `BeaglePlay Debian 11.6 Flasher 2023-03-10
    <https://www.beagleboard.org/distros/beagleplay-debian-11-6-flasher-2023-03-10>`_.

#. Load this image to a microSD card using a tool like Etcher.

#. Insert the microSD card into BeaglePlay.

#. Power BeaglePlay via the USB-C connector.

#. Wait for the LEDs to start blinking, then turn off.

#. Remove power from BeaglePlay.

#. *IMPORTANT* Remove microSD card from BeaglePlay.

#. Apply power to BeaglePlay.

.. note::

   This will flash the CC1352 as well as the eMMC flash on BeaglePlay.

.. todo::

   Describe how to know it is working

Log into BeaglePlay
*********************************

Please either plug in a keyboard, monitor and mouse or :code:`ssh` into the board. We can point
somewhere else for instructions on this. You can also point your web browser to the board to log
into the Visual Studio Code IDE environment.

.. todo::

    A big part of what is missing here is to put your BeaglePlay on the Internet such
    that we can download things in later steps. That has been initially brushed over.

.. _zephyr_flash_radio :

Flash existing IEEE 802.15.4 radio bridge (WPANUSB) firmware
************************************************************

If you've recieved a board fresh from the factory, this is already done and not necessary, unless
you want to restore the contents back to the factory condition.

Background
==========

This `WPANUSB` application was originally developed for radio devices with a USB interface. The CC1352P7
does not have a USB device, so the application was modified to communicate over a UART serial interface.

For the :ref:`beagleconnect-freedom-home`, a USB-to-UART bridge device was used and the USB endpoints
were made compatible with the `WPANUSB linux driver <https://github.com/finikorg/wpanusb>`_ which we
`augmented <https://git.beagleboard.org/beagleconnect/linux/wpanusb/>`_ to support this board. To utilize
the existing `WPANUSB` Zephyr application and this Linux driver, we chose to encode our UART traffic with
`HDLC <https://en.wikipedia.org/wiki/High-Level_Data_Link_Control>`_. This has the advantage of enabing a
serial console interface to the Zephyr shell while WPANUSB-specific traffic is directed to other
`USB endpoints <https://simple.wikipedia.org/wiki/USB#How_USB_works>`_.

For BeaglePlay, the USB-to-UART bridge is not used, but we largely kept the same `WPANUSB` application,
including the HDLC encoding.

.. note::
    Now you know why this WPAN bridge application is called `WPANUSB`, even though USB isn't used!

Steps
=====

#. Ensure the `bcfserial` driver isn't blocking the serial port.

    .. code-block:: bash

        echo "    fdtoverlays /overlays/k3-am625-beagleplay-bcfserial-no-firmware.dtbo" | sudo tee -a /boot/firmware/extlinux/extlinux.conf
        sudo shutdown -r now

    .. note::

        The default password is `temppwd`.

#. Download and flash the `WPANUSB` Zephyr application firmware onto the CC1352P7 on BeaglePlay from the `releases on git.beagleboard.org <https://git.beagleboard.org/beagleconnect/zephyr/zephyr/-/releases>`_ or `distros on www.beagleboard.org/distros <https://www.beagleboard.org/distros>`_.

    .. code-block:: shell-session

        debian@BeaglePlay:~$ wget https://files.beagle.cc/file/beagleboard-public-2021/images/zephyr-beagle-cc1352-0.2.2.zip
        debian@BeaglePlay:~$ unzip zephyr-beagle-cc1352-0.2.2.zip  
        debian@BeaglePlay:~$ build/play/cc2538-bsl.py build/play/wpanusb

#. Ensure the `bcfserial` driver is set to load.

    .. code-block:: bash

        sudo sed -e '/bcfserial-no-firmware/ s/^#*/#/' -i /boot/firmware/extlinux/extlinux.conf
        sudo shutdown -r now

#. Verify the the 6LoWPAN network is up.

    .. callout::

        .. code-block:: shell-session

            debian@BeaglePlay:~$ lsmod | grep bcfserial
            bcfserial              24576  0 <1>
            mac802154              77824  2 wpanusb,bcfserial
            debian@BeaglePlay:~$ ifconfig
            SoftAp0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
                    inet 192.168.8.1  netmask 255.255.255.0  broadcast 192.168.8.255
                    inet6 fe80::3ee4:b0ff:fe7e:b5f7  prefixlen 64  scopeid 0x20<link>
                    ether 3c:e4:b0:7e:b5:f7  txqueuelen 1000  (Ethernet)
                    RX packets 4046  bytes 576780 (563.2 KiB)
                    RX errors 0  dropped 0  overruns 0  frame 0
                    TX packets 4953  bytes 5116336 (4.8 MiB)
                    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

            docker0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
                    inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
                    ether 02:42:f8:29:41:69  txqueuelen 0  (Ethernet)
                    RX packets 0  bytes 0 (0.0 B)
                    RX errors 0  dropped 0  overruns 0  frame 0
                    TX packets 0  bytes 0 (0.0 B)
                    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

            eth0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
                    ether f4:84:4c:fc:5d:13  txqueuelen 1000  (Ethernet)
                    RX packets 0  bytes 0 (0.0 B)
                    RX errors 0  dropped 0  overruns 0  frame 0
                    TX packets 0  bytes 0 (0.0 B)
                    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

            lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
                    inet 127.0.0.1  netmask 255.0.0.0
                    inet6 ::1  prefixlen 128  scopeid 0x10<host>
                    loop  txqueuelen 1000  (Local Loopback)
                    RX packets 246239  bytes 19948296 (19.0 MiB)
                    RX errors 0  dropped 0  overruns 0  frame 0
                    TX packets 246239  bytes 19948296 (19.0 MiB)
                    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

            lowpan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1280 <2>
                    inet6 fe80::200:0:0:0  prefixlen 64  scopeid 0x20<link> <3>
                    inet6 2001:db8::2  prefixlen 64  scopeid 0x0<global> <4>
                    unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 1000  (UNSPEC)
                    RX packets 107947  bytes 6629290 (6.3 MiB)
                    RX errors 0  dropped 0  overruns 0  frame 0
                    TX packets 2882  bytes 179511 (175.3 KiB) <5>
                    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

            usb0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
                    inet 192.168.7.2  netmask 255.255.255.0  broadcast 192.168.7.255
                    inet6 fe80::1eba:8cff:fea2:ed6b  prefixlen 64  scopeid 0x20<link>
                    ether 1c:ba:8c:a2:ed:6b  txqueuelen 1000  (Ethernet)
                    RX packets 9858  bytes 2638440 (2.5 MiB)
                    RX errors 0  dropped 0  overruns 0  frame 0
                    TX packets 4155  bytes 1454082 (1.3 MiB)
                    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

            usb1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
                    inet 192.168.6.2  netmask 255.255.255.0  broadcast 192.168.6.255
                    inet6 fe80::1eba:8cff:fea2:ed6d  prefixlen 64  scopeid 0x20<link>
                    ether 1c:ba:8c:a2:ed:6d  txqueuelen 1000  (Ethernet)
                    RX packets 469614  bytes 35385636 (33.7 MiB)
                    RX errors 0  dropped 0  overruns 0  frame 0
                    TX packets 365548  bytes 66523708 (63.4 MiB)
                    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

            wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
                    inet 192.168.0.161  netmask 255.255.255.0  broadcast 192.168.0.255
                    inet6 fe80::3ee4:b0ff:fe7e:b5f6  prefixlen 64  scopeid 0x20<link>
                    inet6 2601:408:c083:b6c0::d00d  prefixlen 128  scopeid 0x0<global>
                    ether 3c:e4:b0:7e:b5:f6  txqueuelen 1000  (Ethernet)
                    RX packets 3188898  bytes 678154090 (646.7 MiB)
                    RX errors 0  dropped 0  overruns 0  frame 0
                    TX packets 1162074  bytes 293237366 (279.6 MiB)
                    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

            wpan0: flags=195<UP,BROADCAST,RUNNING,NOARP>  mtu 123 <6>
                    unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 300  (UNSPEC)
                    RX packets 108495  bytes 2539160 (2.4 MiB)
                    RX errors 0  dropped 0  overruns 0  frame 0
                    TX packets 2888  bytes 140523 (137.2 KiB)
                    TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

        .. annotations::

            <1> You'll want to see that the `bcfserial` driver has been loaded.

            <2> There should be a `lowpan0` interface.

            <3> There should be a link-local address for `lowpan0`.

            <4> There should be a global address for `lowpan0`.

            <5> Seeing some packets have been transmitted can give you some confidence.

            <6> The `wpan0` interface should be there, but we have a 6LoWPAN adapter on top of it.


.. note::

   You may find `Linux-WPAN.org <https://linux-wpan.org/documentation.html>`_ useful.


.. _beagleplay-zephyr-development-setup:

Setup Zephyr development on BeaglePlay
*********************************************

#. Download and setup Zephyr for BeaglePlay

    .. code-block:: bash
        
        cd
        sudo apt update
        sudo apt install --no-install-recommends -y \
            gperf \
            ccache dfu-util \
            libsdl2-dev \
            libxml2-dev libxslt1-dev libssl-dev libjpeg62-turbo-dev libmagic1 \
            libtool-bin autoconf automake libusb-1.0-0-dev \
            python3-tk python3-virtualenv
        wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.15.1/zephyr-sdk-0.15.1_linux-aarch64_minimal.tar.gz
        tar xf zephyr-sdk-0.15.1_linux-aarch64_minimal.tar.gz
        rm zephyr-sdk-0.15.1_linux-aarch64_minimal.tar.gz
        ./zephyr-sdk-0.15.1/setup.sh -t arm-zephyr-eabi -c
        west init -m https://git.beagleboard.org/beagleconnect/zephyr/zephyr --mr sdk zephyr-beagle-cc1352-sdk
        cd $HOME/zephyr-beagle-cc1352-sdk
        python3 -m virtualenv zephyr-beagle-cc1352-env
        echo "export ZEPHYR_TOOLCHAIN_VARIANT=zephyr" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo "export ZEPHYR_SDK_INSTALL_DIR=$HOME/zephyr-sdk-0.15.1" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo "export ZEPHYR_BASE=$HOME/zephyr-beagle-cc1352-sdk/zephyr" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo 'export PATH=$HOME/zephyr-beagle-cc1352-sdk/zephyr/scripts:$PATH' >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo "export BOARD=beagleplay" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        source $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        west update
        west zephyr-export
        pip3 install -r zephyr/scripts/requirements-base.txt

#. Activate the Zephyr build environment

    If you exit and come back, you'll need to reactivate your Zephyr build environment.

    .. code-block:: bash
        
        source $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate

#. Verify Zephyr setup for BeaglePlay

    .. code-block:: shell-session

        (zephyr-beagle-cc1352-env) debian@BeaglePlay:~$ cmake --version
        cmake version 3.22.1

        CMake suite maintained and supported by Kitware (kitware.com/cmake).
        (zephyr-beagle-cc1352-env) debian@BeaglePlay:~$ python3 --version
        Python 3.9.2
        (zephyr-beagle-cc1352-env) debian@BeaglePlay:~$ dtc --version
        Version: DTC 1.6.0
        (zephyr-beagle-cc1352-env) debian@BeaglePlay:~$ west --version
        West version: v0.14.0
        (zephyr-beagle-cc1352-env) debian@BeaglePlay:~$ ./zephyr-sdk-0.15.1/arm-zephyr-eabi/bin/arm-zephyr-eabi-gcc --version
        arm-zephyr-eabi-gcc (Zephyr SDK 0.15.1) 12.1.0
        Copyright (C) 2022 Free Software Foundation, Inc.
        This is free software; see the source for copying conditions.  There is NO
        warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

 
Build applications for BeaglePlay CC1352
*********************************************

Now you can build various Zephyr applications

#. Build and flash Blinky example

    .. code-block:: bash

        cd $HOME/zephyr-beagle-cc1352-sdk/zephyr
        west build -d build/play_blinky samples/basic/blinky
        west flash -d build/play_blinky

#. Try out Micropython

    .. code-block:: bash

        cd
        git clone -b beagleplay-cc1352 https://git.beagleboard.org/beagleplay/micropython
        cd micropython
        west build -d play ports/zephyr
        west flash -d play
        tio /dev/ttyS4

Build applications for BeagleConnect Freedom
*********************************************

#. Build and flash Blinky example

    .. code-block:: bash

        cd $HOME/zephyr-beagle-cc1352-sdk/zephyr
        west build -d build/freedom_blinky -b beagleconnect_freedom samples/basic/blinky
        west flash -d build/freedom_blinky

#. Try out Micropython

    .. code-block:: bash

        cd
        git clone -b beagleplay-cc1352 https://git.beagleboard.org/beagleplay/micropython
        cd micropython
        west build -d freedom -b beagleconnect_freedom ports/zephyr
        west flash -d freedom
        tio /dev/ttyACM0


.. important::

    Nothing below here is tested

.. todo::

    .. code-block:: bash

        west build -d build/sensortest zephyr/samples/boards/beagle_bcf/sensortest -- -DOVERLAY_CONFIG=overlay-subghz.conf


    .. code-block:: bash

        west build -d build/wpanusb modules/lib/wpanusb_bc -- -DOVERLAY_CONFIG=overlay-subghz.conf


    .. code-block:: bash

        west build -d build/bcfserial modules/lib/wpanusb_bc -- -DOVERLAY_CONFIG=overlay-bcfserial.conf -DDTC_OVERLAY_FILE=bcfserial.overlay


    .. code-block:: bash

        west build -d build/greybus modules/lib/greybus/samples/subsys/greybus/net -- -DOVERLAY_CONFIG=overlay-802154-subg.conf


Flash applications to BeagleConnect Freedom
===========================================

And then you can flash the BeagleConnect Freedom boards over USB

#. Make sure you are in Zephyr directory
    .. code-block:: bash

        cd $HOME/bcf-zephyr

#. Flash Blinky
    .. code-block:: bash

        cc2538-bsl.py build/blinky

Debug applications over the serial terminal
===========================================

.. todo::

   Describe how to handle the serial connection
