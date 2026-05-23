.. _beaglebone-blue-one-liner-tests:

BeagleBone Blue tests
#######################

ADC
****

-  `Grove Rotary Angle
   Sensor <http://wiki.seeed.cc/Grove-Rotary_Angle_Sensor/>`__
   See output on adc_1
   `source <https://git.beagleboard.org/beagleboard/librobotcontrol/-/blob/v1.1/examples/src/rc_test_adc.c>`__

.. code:: bash

      rc_test_adc

GP0
****

-  Grove single GPIO output modules like `LED Socket
   Kit <http://wiki.seeed.cc/Grove-LED_Socket_Kit/>`__

.. code:: bash

      cd /sys/class/gpio;echo 49 >export;cd gpio49;echo out >direction;while sleep 1;do echo 0 >value;sleep 1;echo 1 >value;done

-  Grove single GPIO input modules like `IR Distance
   Interrupter <http://wiki.seeed.cc/Grove-IR_Distance_Interrupter_v1.2/>`__
   or `Touch Sensor <http://wiki.seeed.cc/Grove-Touch_Sensor/>`__

.. code:: bash

      cd /sys/class/gpio;echo 49 >export;cd gpio49;echo in >direction;watch -n0 cat value

GP1
****

-  Grove single GPIO output modules like `LED Socket
   Kit <http://wiki.seeed.cc/Grove-LED_Socket_Kit/>`__

.. code:: bash

      cd /sys/class/gpio;echo 97 >export;cd gpio97;echo out >direction;while sleep 1;do echo 0 >value;sleep 1;echo 1 >value;done

-  Grove single GPIO input modules like `IR Distance
   Interrupter <http://wiki.seeed.cc/Grove-IR_Distance_Interrupter_v1.2/>`__
   or `Touch Sensor <http://wiki.seeed.cc/Grove-Touch_Sensor/>`__

.. code:: bash

      cd /sys/class/gpio;echo 97 >export;cd gpio97;echo in >direction;watch -n0 cat value

UT1
****

-  `Grove GPS <http://wiki.seeed.cc/Grove-GPS/>`__

.. code:: bash

      tio /dev/ttyO1 -b 9600

GPS
*****

-  `GPS Receiver - EM-506 <https://www.sparkfun.com/products/12751>`__

.. code:: bash

      tio /dev/ttyO2 -b 4800

.. _beaglebone-blue-one-liner-tests-i2c:

I2C
*****

.. _grove_i2c_modules:

Grove I2C modules
==================

The Linux kernel source has some `basic IIO SYSFS interface
documentation <https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-bus-iio>`__
which might provide a little help for understanding reading these
entries. The ELC2017 conference also had `an IIO
presentation <http://elinux.org/images/b/ba/ELC_2017_-_Industrial_IO_and_You-_Nonsense_Hacks%21.pdf>`__.

-  `Digital Light Sensor <http://wiki.seeed.cc/Grove-Digital_Light_Sensor/>`__

.. code:: bash

      cd /sys/bus/i2c/devices/i2c-1;echo tsl2561 0x29 >new_device;watch -n0 cat 1-0029/iio\:device0/in_illuminance0_input

-  `Temperature & Humidity
   Sensor <http://wiki.seeed.cc/Grove-TemptureAndHumidity_Sensor-High-Accuracy_AndMini-v1.0/>`__

.. code:: bash

      cd /sys/bus/i2c/devices/i2c-1;echo th02 0x40 >new_device;watch -n0 cat 1-0040/iio\:device0/in_temp_raw

Motors
*******

.. code:: bash

   rc_test_motors
