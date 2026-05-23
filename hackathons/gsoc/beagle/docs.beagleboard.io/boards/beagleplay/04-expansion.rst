.. _beagleplay-expansion:

Expansion
#########

.. todo::

   Add information on building expansion hardware for BeaglePlay.

mikroBUS
*********

The mikroBUS header provides several GPIO pins as well as UART, I2C, SPI, PWM and an Analog Input. 

By default, the port is controlled by a mikroBUS driver that helps with auto-detecting MikroE Click Board that feature `ClickID <https://www.mikroe.com/clickid>`_. 
This does however mean that if you want to manually control the port, you may need to first disable the driver.

To disable the driver, do the following - TODO

Grove
******

The Grove port on BeaglePlay exposes one of the SoC I2C Ports as well as an analog input. 

It maps directly in linux as /dev/I2C-TODO or as the following alias /dev/play/grove

QWIIC
******

The QWIIC port on BeaglePlay exposes one of the SoC I2C Ports. 

It maps directly in linux as `/dev/I2C-2` or as the following alias `/dev/play/qwiic`


CSI
***

The AM62x SoC (and by extension BeaglePlay) does not feature on-board ISP (Image Signal Processor) hardware, and as such, Raw-Bayer CSI Sensors must be pre-processed into normal images by the A53 cores.

To avoid performance penalties related to the approach above, it is recommended to use a sensor with a built-in ISP, such as the OV5640 which is supported out of box.

The `PCam5C from Digilent <https://digilent.com/shop/pcam-5c-5-mp-fixed-focus-color-camera-module/>`_ is one CSI camera that features this sensor.


.. note:: Since BeaglePlay uses a 22-pin CSI connector, a 15 pin to 22 pin CSI adapter may also be required `such as this one <https://www.uctronics.com/arducam-15-pin-1-0mm-pitch-to-22-pin-0-5mm-camera-cable-for-raspberry-pi-zero-version-1-3-specific-pack-of-2.html>`_


Once installed, there are some software changes required to load the device driver at boot for the OV5640. 

We will need to modify the following file: /boot/firmware/extlinux/extlinux.conf

We will add the following line to load the OV5640 DTBO:

.. code:: bash

   fdtoverlays /overlays/k3-am625-beagleplay-csi2-ov5640.dtbo

Then you can reboot: sudo reboot

Camera should now work, you can use mplayer to test.

.. code:: bash

   sudo apt-get install -y mplayer

   mplayer tv: // -tv driver=v4l2:device=/dev/video0:width=640:height=480:fps=30:outfmt=yuy2


OLDI
****

BeaglePlay brings out two OLDI (LVDS) channels, each with up to four data lanes and one clock lane to support 21/28-bit serialized RGB pixel data and synchronization transmissions. The first port, OLDI0, consists of OLDI0_A0-3/CLK0 and corresponds to odd pixels, while the second port, OLDI1, consists of OLDI0_A4-7/CLK1 and corresponds to even pixels.

It is pin compatible with the following two displays from Lincoln Technology Solutions:

Both displays have the following features and only differ in bezzle type:

* **Resolution** - 1920x1200 (16:10)
*  **LCD Size (diagonal)** - 10.1"
* **Refresh Rate** - 60Hz
* **Brightness** - 1000nit
* **Pannel Type** - Edge-lit IPS 
* **Touch Enabled** - Yes, Capacitive
* **Connector** - 40 pin FFC ribbon cable

`A "Flush Coverglass" Version <https://www.digikey.com/en/products/detail/lincoln-technology-solutions/LCDK185-101CTL1ARNTTR1-0/20485318?s=N4IgTCBcDaIDIGEAiBpAjADgKwgLoF8g>`_
`A "Oversized Cover Glass" Version - similar in style to a Tablet Display <https://www.digikey.com/en/products/detail/lincoln-technology-solutions/LCDK217-101CTL1ARNTTR1-0/20485319?s=N4IgTCBcDaIDIGEAiBpMBGA7CAugXyA>`_

To enable OLDI display support, modify the following file: /boot/firmware/extlinux/extlinux.conf

Then, add the following line to load the Lincoln LCD185 OLDI DTBO: 

.. code:: bash

   fdtoverlays /overlays/k3-am625-beagleplay-lt-lcd185.dtbo

Your /boot/firmware/extlinux/extlinux.conf file should look something like this:

.. code:: bash

   label Linux eMMC
      kernel /Image
      append root=/dev/mmcblk0p2 ro rootfstype=ext4 rootwait net.ifnames=0 systemd.unified_cgroup_hierarchy=false quiet
      fdtdir /
      fdtoverlays /overlays/k3-am625-beagleplay-lt-lcd185.dtbo
      initrd /initrd.img


