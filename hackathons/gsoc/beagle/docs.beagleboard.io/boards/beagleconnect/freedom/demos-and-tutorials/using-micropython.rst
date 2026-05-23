.. _beagleconnect-freedom-using-micropython:

Using Micropython
#################

.. important::

   Currently under development

Micropython is a great way to get started developing with BeagleConnect Freedom quickly.

Flashed firmware
****************

BeagleConnect Freedom initial production firmware is release 0.0.3 of our own fork of Micropython.

https://git.beagleboard.org/beagleconnect/zephyr/micropython/-/releases/0.0.3

You can verify this version by using ``mcumgr`` over a UDP connection or ``mcuboot`` over the serial console shell.

Latest releases are part of our Zephyr SDK releases.

https://git.beagleboard.org/beagleconnect/zephyr/zephyr/-/releases

Examples
********

0.0.3
=====

The first boards were flashed with this firmware.

.. code-block:: shell-session

        debian@BeaglePlay:~$ sudo systemd-resolve --set-mdns=yes --interface=lowpan0
        debian@BeaglePlay:~$ avahi-browse -r -t _zephyr._tcp
        + lowpan0 IPv6 zephyr                                        _zephyr._tcp         local
        = lowpan0 IPv6 zephyr                                        _zephyr._tcp         local
           hostname = [zephyr.local]
           address = [fe80::3265:842a:4b:1200]
           port = [12345]
           txt = []
        debian@BeaglePlay:~$ avahi-resolve -6 -n zephyr.local
        zephyr.local	fe80::ec0f:7a22:4b:1200
        debian@BeaglePlay:~$ mcumgr conn add bcf0 type="udp" connstring="[fe80::3265:842a:4b:1200%lowpan0]:1337"
        Connection profile bcf0 successfully added
        debian@BeaglePlay:~$ mcumgr -c bcf0 image list
        Images:
         image=0 slot=0
            version: hu.hu.hu
            bootable: true
            flags: active confirmed
            hash: 3697bcef05a6becda7dc14150d46c05dbed5fa78633657b20cf34e1418affee9
        Split status: N/A (0)
        debian@BeaglePlay:~$ mcumgr -c bcf0 shell exec "device list"
        status=0

        devices:
        - GPIO_0 (READY)
        - random@40028000 (READY)
        - UART_1 (READY)
        - UART_0 (READY)
        - i2c@40002000 (READY)
        - I2C_0S (READY)
          requires: GPIO_0
          requires: i2c@40002000
        - flash-controller@40030000 (READY)
        - spi@40000000 (READY)
          requires: GPIO_0
        - ieee802154g (READY)
        - gd25q16c@0 (READY)
          requires: spi@40000000
        - leds (READY)
        - HDC2010-HUMIDITY (READY)
          requires: I2C_0S
        - 
        debian@BeaglePlay:~$ mcumgr -c bcf0 shell exec "net iface"
        status=0

        Hostname: zephyr


        Interface 0x20002de4 (IEEE 802.15.4) [1]
        ========================================
        Link addr : 30:65:84:2A:00:4B:12:00
        MTU       : 125
        Flags     : AUTO_START,IPv6
        IPv6 unicast addresses (max 3):
                fe80::3265:842a:4b:1200 autoconf preferred infinite
                2001:db8::1 manual preferred infinite
        IPv6 multicast addresses (max 4):
                ff02::1
                ff02::1:ff4b:1200
                ff02::1:ff00:1
        debian@BeaglePlay:~$ tio /dev/ttyACM0
        [tio 07:32:17] tio v1.32
        [tio 07:32:17] Press ctrl-t q to quit
        [tio 07:32:17] Connected
        gd25q16c@0: SFDP v 1.0 AP ff with 2 PH
        I: PH0: ff00 rev 1.0: 9 DW @ 30
        I: gd25q16c@0: 2 MiBy flash
        I: PH1: ffc8 rev 1.0: 3 DW @ 60
        *** Booting Zephyr OS build zephyr-v3.2.0-3470-g14e193081b1f ***
        I: Starting bootloader
        I: Primary image: magic=unset, swap_type=0x1, copy_done=0x3, image_ok=0x3
        I: Scratch: magic=unset, swap_type=0x1, copy_done=0x3, image_ok=0x3
        I: Boot source: primary slot
        I: Swap type: test
        I: Bootloader chainload address offset: 0x20000
        I: Jumping to the first image slot


        [00:00:00.001,647] <inf> spi_nor: gd25q16c@0: SFDP v 1.0 AP ff with 2 PH
        [00:00:00.001,647] <inf> spi_nor: PH0: ff00 rev 1.0: 9 DW @ 30
        [00:00:00.001,983] <in
        >>> 

Press reset

.. code-block:: shell-session

        I: gd25q16c@0: SFDP v 1.0 AP ff with 2 PH
        I: PH0: ff00 rev 1.0: 9 DW @ 30
        I: gd25q16c@0: 2 MiBy flash
        I: PH1: ffc8 rev 1.0: 3 DW @ 60
        *** Booting Zephyr OS build zephyr-v3.2.0-3470-g14e193081b1f ***
        I: Starting bootloader
        I: Primary image: magic=unset, swap_type=0x1, copy_done=0x3, image_ok=0x3
        I: Scratch: magic=unset, swap_type=0x1, copy_done=0x3, image_ok=0x3
        I: Boot source: primary slot
        I: Swap type: test
        I: Bootloader chainload address offset: 0x20000
        I: Jumping to the first image slot


        [00:00:00.001,495] <inf> spi_nor: gd25q16c@0: SFDP v 1.0 AP ff with 2 PH
        [00:00:00.001,525] <inf> spi_nor: PH0: ff00 rev 1.0: 9 DW @ 30
        [00:00:00.001,800] <inf> spi_nor: gd25q16c@0: 2 MiBy flash
        [00:00:00.001,831] <inf> spi_nor: PH1: ffc8 rev 1.0: 3 DW @ 60
        uart:~$ build time: Feb 22 2023 07:13:09MicroPython v1.19.1 on 2023-02-22; zephyr-beagleconnect_freedom with unknown-cpu
        Type "help()" for more information.
        >>> help()
        Welcome to MicroPython!

        Control commands:
          CTRL-A        -- on a blank line, enter raw REPL mode
          CTRL-B        -- on a blank line, enter normal REPL mode
          CTRL-C        -- interrupt a running program
          CTRL-D        -- on a blank line, do a soft reset of the board
          CTRL-E        -- on a blank line, enter paste mode

        For further help on a specific object, type help(obj)

        See https://beagleconnect.org/micropython for examples.
        >>> import zsensor
        >>> light=zsensor.Sensor("OPT3001-LIGHT")
        >>> humidity=zsensor.Sensor("HDC2010-HUMIDITY")
        >>> light.measure()
        >>> light.get_float(zsensor.LIGHT)
        35.94
        >>> humidity.measure()
        >>> humidity.get_float(zsensor.HUMIDITY)
        24.32861
        >>> humidity.get_float(zsensor.AMBIENT_TEMP)
        22.37704
        >>> dir(zsensor)
        ['__name__', 'ACCEL_X', 'ACCEL_Y', 'ACCEL_Z', 'ALTITUDE', 'AMBIENT_TEMP', 'BLUE', 'CO2', 'DIE_TEMP', 'DISTANCE', 'GAS_RES', 'GREEN', 'GYRO_X', 'GYRO_Y', 'GYRO_Z', 'HUMIDITY', 'IR', 'LIGHT', 'MAGN_X', 'MAGN_Y', 'MAGN_Z', 'PM_10', 'PM_1_0', 'PM_2_5', 'PRESS', 'PROX', 'RED', 'Sensor', 'VOC', 'VOLTAGE']
        >>> import os
        >>> with open('/flash/test.txt', 'w') as f:
        ...     f.write("My test.txt\n")
        ...     ^H
        12
        >>> print(open('/flash/test.txt').read())
        My test.txt

        >>> import socket
        >>> sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        >>> sock.bind(('ff02::1', 9999))
        >>> for i in range(3):
        ...     data, sender = sock.recvfrom(1024)
        ...     print(str(sender) + '  ' + repr(data))
        ...     ^H
        ('fe80::ec0f:7a22:4b:1200', <>, 0, 7)  b'4h:32.71;4t:17.29;'
        ('fe80::ec0f:7a22:4b:1200', <>, 0, 7)  b'2l:0.35;'
        ('fe80::ec0f:7a22:4b:1200', <>, 0, 7)  b'4h:32.71;4t:17.29;'
        >>> import machine
        >>> AN=machine.Pin(("GPIO_0", 23), machine.Pin.OUT)
        >>> AN.init(machine.Pin.OUT, machine.Pin.PULL_UP, value=1)
        >>> LNK_LED=machine.Pin(("GPIO_0", 18), machine.Pin.OUT)
        >>> LNK_LED.init(machine.Pin.OUT, machine.Pin.PULL_UP, value=1)
        >>> LNK_LED.off()
        >>> LNK_LED.on()
        >>>
        ^Tq
        [tio 07:40:16] Disconnected
        debian@BeaglePlay:~$

0.2.2
=====

.. todo::

   Need to describe functionality of 0.2.2

Updating
********

Look for the latest firmware release on https://www.beagleboard.org/distros or on https://beagleconnect.org.

Download, unzip and flash the ``micropython-w-boot`` image.

.. code-block:: bash

   wget https://files.beagle.cc/file/beagleboard-public-2021/images/zephyr-beagle-cc1352-0.2.2.zip
   unzip zephyr-beagle-cc1352-0.2.2.zip
   ./build/freedom/cc2538-bsl.py build/freedom/micropython-w-boot

Contributing
************

Repository: https://git.beagleboard.org/beagleconnect/zephyr/micropython
