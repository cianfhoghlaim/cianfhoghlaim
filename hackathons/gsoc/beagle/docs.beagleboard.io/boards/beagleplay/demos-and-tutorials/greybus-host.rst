.. _greybus-host:

BeagleConnect™ Greybus demo using BeagleConnect™ Freedom and BeaglePlay
#######################################################################

BeaglePlay CC1352 Firmware
**************************

Build (Download and Setup Zephyr for BeaglePlay)
================================================

#. Install prerequisites

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

#. Download the latest Zephyr Release, extract it and cleanup

    .. code-block:: bash

        sudo wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.16.3/zephyr-sdk-0.16.3_linux-aarch64_minimal.tar.xz
        tar xf zephyr-sdk-0.16.3_linux-aarch64_minimal.tar.xz
        rm zephyr-sdk-0.16.3_linux-aarch64_minimal.tar.xz


#. Run the Zephyr SDK Setup Script

    .. code-block:: bash

        ./zephyr-sdk-0.16.3/setup.sh -t arm-zephyr-eabi -c

#. Download and Initialize `West <https://docs.zephyrproject.org/latest/develop/west/index.html/>`_. (Zephyr's meta-tool)

    .. note:: 
        
        You may want to add `/home/debian/.local/bin` to your `.bashrc` file to make the West command available after a reboot

    .. code-block:: bash

        pip3 install --user -U west
        export PATH="/home/debian/.local/bin:$PATH"
        west init -m https://git.beagleboard.org/beagleconnect/zephyr/zephyr --mr sdk-next zephyr-beagle-cc1352-sdk
        cd $HOME/zephyr-beagle-cc1352-sdk


#. Setup a Python Virtual Environment and add our PATH Variables

    .. code-block:: bash

        virtualenv zephyr-beagle-cc1352-env
        echo "export ZEPHYR_TOOLCHAIN_VARIANT=zephyr" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo "export ZEPHYR_SDK_INSTALL_DIR=$HOME/zephyr-sdk-0.16.3" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo "export ZEPHYR_BASE=$HOME/zephyr-beagle-cc1352-sdk/zephyr" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo 'export PATH=$HOME/zephyr-beagle-cc1352-sdk/zephyr/scripts:$PATH' >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo "export BOARD=beagleplay_cc1352" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        source $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate


#. Update West

    .. code-block:: bash

        west update
        west zephyr-export

#. Install Python Prerequisites

    .. code-block:: bash
        
        pip3 install -r zephyr/scripts/requirements-base.txt

#. Activate the Zephyr build environment

    NOTE - If you exit and come back, you'll need to reactivate your Zephyr build environment.

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

        (zephyr-beagle-cc1352-env) debian@BeaglePlay:~$ ./zephyr-sdk-0.16.3/arm-zephyr-eabi/bin/arm-zephyr-eabi-gcc --version
        arm-zephyr-eabi-gcc (Zephyr SDK 0.16.3) 12.1.0

        Copyright (C) 2022 Free Software Foundation, Inc.
        This is free software; see the source for copying conditions.  There is NO
        warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

#. Clone CC1352 Firmware at top level: https://git.beagleboard.org/gsoc/greybus/cc1352-firmware

    .. code-block:: bash

        cd ~
        git clone https://git.beagleboard.org/gsoc/greybus/cc1352-firmware

#. Build the Firmware

    .. code-block:: bash

        west build -b beagleplay_cc1352 -p always cc1352-firmware

#. You can now find the built firmware at `build/zephyr/zephyr.bin`

Flash
=====
#. Ensure the `gb-beagleplay` driver isn't blocking the serial port.

    .. code-block:: shell-session

        debian@BeaglePlay:~$ echo "    fdtoverlays /overlays/k3-am625-beagleplay-bcfserial-no-firmware.dtbo" | sudo tee -a /boot/firmware/extlinux/extlinux.conf
        debian@BeaglePlay:~$ sudo shutdown -r now

    .. note::

        The default password is `temppwd`.

#. Clone cc1352-flasher

    .. code-block:: bash

        cd
        git clone https://git.beagleboard.org/beagleconnect/cc1352-flasher.git

#. Flash Firmware

    .. code-block:: bash

        python $HOME/cc1352-flasher --beagleplay $HOME/zephyr-beagle-cc1352-sdk/build/zephyr/zephyr.bin

#. Ensure the `gb-beagleplay` driver is set to load.

    .. code-block:: bash

        sudo sed -e '/bcfserial-no-firmware/ s/^#*/#/' -i /boot/firmware/extlinux/extlinux.conf
        sudo shutdown -r now

Building gb-beagleplay Kernel Module
**************************************

.. note::

    `gb-beagleplay` is still not merged upstream and thus needs to be built seperately. This should not be required in the future.

#. Disable bcfserial driver. Add ``quiet module_blacklist=bcfserial`` to kernel parameters at ``/boot/firmware/extlinux/extlinux.conf`` (line 2) as shown below.

  .. callout::

    .. code-block:: shell-session

        label Linux eMMC
            kernel /Image
            append root=/dev/mmcblk0p2 ro rootfstype=ext4 rootwait net.ifnames=0 quiet module_blacklist=bcfserial <1>
            fdtdir /
            #fdtoverlays /overlays/<file>.dtbo
            #fdtoverlays /overlays/k3-am625-beagleplay-bcfserial-no-firmware.dtbo
            fdtoverlays /overlays/k3-am625-beagleplay-release-mikrobus.dtbo
            initrd /initrd.img
        
    .. annotations::

        <1> ``quiet module_blacklist=bcfserial`` has been added to this line

#. Reboot

    .. code-block:: shell-session

       debian@BeaglePlay:~$ sudo shutdown -r now

#. Download the upstream module

    .. code-block:: shell-session

        debian@BeaglePlay:~$ git clone https://git.beagleboard.org/gsoc/greybus/beagleplay-greybus-driver.git
        debian@BeaglePlay:~$ cd beagleplay-greybus-driver

#. Install dependencies

    .. code-block:: shell-session

        debian@BeaglePlay:~$ sudo apt install linux-headers-$(uname -r)

#. Build Kernel moudle

    .. code-block:: shell-session

        debian@BeaglePlay:~/beagleplay-greybus-driver$ make
        make -C /lib/modules/5.10.168-ti-arm64-r111/build M=/home/debian/beagleplay-greybus-driver modules
        make[1]: Entering directory '/usr/src/linux-headers-5.10.168-ti-arm64-r111'
          CC [M]  /home/debian/beagleplay-greybus-driver/gb-beagleplay.o
          MODPOST /home/debian/beagleplay-greybus-driver/Module.symvers
          CC [M]  /home/debian/beagleplay-greybus-driver/gb-beagleplay.mod.o
          LD [M]  /home/debian/beagleplay-greybus-driver/gb-beagleplay.ko
        make[1]: Leaving directory '/usr/src/linux-headers-5.10.168-ti-arm64-r111'

Flashing BeagleConnect Freedom Greybus Firmware
***********************************************

#. Connect BeagleConnect Freedom to BeaglePlay
#. Build the BeagleConnect Freedom firmware

    .. code-block:: bash

        west build -b beagleconnect_freedom modules/greybus/samples/subsys/greybus/net/ -p -- -DOVERLAY_CONFIG=overlay-802154-subg.conf

#. Flash the BeagleConnect Freedom

    .. code-block:: bash

        west flash

Run the Demo
*************

#. Connect BeagleConnect Freedom.
#. See shell output using `tio`

    .. code-block:: bash
    
        tio /dev/ACM0

#. Press the Reset button on BeagleConnect Freedom

#. Verify that greybus is working by checking the `tio` output. It should look as follows:

    .. code-block:: shell-session

        [00:00:00.000,976] <dbg> greybus_platform_bus: greybus_init: probed greybus: 0 major: 0 minor: 1
        [00:00:00.001,068] <dbg> greybus_platform_string: greybus_string_init: probed greybus string 4: hdc2010
        [00:00:00.001,129] <dbg> greybus_platform_string: greybus_string_init: probed greybus string 3: opt3001
        [00:00:00.001,190] <dbg> greybus_platform_string: greybus_string_init: probed greybus string 2: Greybus Service Sample Application
        [00:00:00.001,251] <dbg> greybus_platform_string: greybus_string_init: probed greybus string 1: Zephyr Project RTOS
        [00:00:00.001,251] <dbg> greybus_platform_interface: greybus_interface_init: probed greybus interface 0
        [00:00:00.001,281] <dbg> greybus_platform_bundle: greybus_bundle_init: probed greybus bundle 1: class: 10
        [00:00:00.001,312] <dbg> greybus_platform_bundle: greybus_bundle_init: probed greybus bundle 0: class: 0
        [00:00:00.001,342] <dbg> greybus_platform_control: greybus_control_init: probed cport 0: bundle: 0 protocol: 0
        [00:00:00.001,434] <dbg> greybus_platform: gb_add_cport_device_mapping: added mapping between cport 1 and device gpio@40022000
        [00:00:00.001,464] <dbg> greybus_platform_gpio_control: greybus_gpio_control_init: probed cport 1: bundle: 1 protocol: 2
        [00:00:00.001,556] <dbg> greybus_platform: gb_add_cport_device_mapping: added mapping between cport 2 and device sensor-switch
        [00:00:00.001,556] <dbg> greybus_platform_i2c_control: greybus_i2c_control_init: probed cport 2: bundle: 1 protocol: 3
        *** Booting Zephyr OS build bcf-sdk-0.2.1-3384-ge76584f824c8 ***
        [00:00:00.009,704] <dbg> greybus_service: greybus_service_init: Greybus initializing..
        [00:00:00.009,765] <dbg> greybus_manifest: identify_descriptor: cport_id = 0
        [00:00:00.009,796] <dbg> greybus_manifest: identify_descriptor: cport_id = 1
        [00:00:00.009,826] <dbg> greybus_manifest: identify_descriptor: cport_id = 2
        [00:00:00.009,857] <dbg> greybus_transport_tcpip: gb_transport_backend_init: Greybus TCP/IP Transport initializing..
        [00:00:00.010,101] <inf> greybus_transport_tcpip: CPort 0 mapped to TCP/IP port 4242
        [00:00:00.014,709] <inf> greybus_transport_tcpip: CPort 1 mapped to TCP/IP port 4243
        [00:00:00.014,953] <inf> greybus_transport_tcpip: CPort 2 mapped to TCP/IP port 4244
        [00:00:00.015,075] <inf> greybus_transport_tcpip: Greybus TCP/IP Transport initialized
        [00:00:00.015,136] <inf> greybus_manifest: Registering CONTROL greybus driver.
        [00:00:00.015,167] <dbg> greybus: _gb_register_driver: Registering Greybus driver on CP0
        [00:00:00.015,411] <inf> greybus_manifest: Registering GPIO greybus driver.
        [00:00:00.015,411] <dbg> greybus: _gb_register_driver: Registering Greybus driver on CP1
        [00:00:00.015,625] <inf> greybus_manifest: Registering I2C greybus driver.
        [00:00:00.015,625] <dbg> greybus: _gb_register_driver: Registering Greybus driver on CP2
        [00:00:00.015,777] <inf> greybus_service: Greybus is active

#. Load gb-beagleplay

    .. code-block:: shell-session

        debian@BeaglePlay:~$ sudo insmod $HOME/beagleplay-greybus-driver/gb-beagleplay.ko

#. Check `iio_device` to verify that greybus node has been detected:

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

