Features
#########

BB-Config v1.x
***************

PRU Enable/Disable
===================
- Enable/Disable PRU

.. image:: images/pru.png
   :align: center
   :alt: pru


GPIO
=====
- Turn On/Off gpio

GPIO Menu
----------

.. image:: images/gpio.png
   :align: center
   :alt: gpio menu


GPIO Setting
-------------

.. image:: images/gpio2.png
   :align: center
   :alt: gpio setting


EMMC and MicroSD Stats
=======================
- Storage stats & grow partition

.. image:: images/emmc.png
   :align: center
   :alt: emmc


LEDs
=====
- Config board build in LEDs

.. image:: images/leds.png
   :align: center
   :alt: leds


Password
=========
- Change users password

.. image:: images/password.png
   :align: center
   :alt: password


SSH
====
- Enable/Disable SSH

.. image:: images/ssh.png
   :align: center
   :alt: ssh


WiFi
=====
- Connect to Wi-Fi

.. image:: images/wifi.png
   :align: center
   :alt: WiFi


Internet Sharing and Client Config
===================================

.. image:: images/ics.png
   :align: center
   :alt: ics


- Note: You'll have to configure your host Following is an example script:

.. code:: bash
   
    echo 1 > /proc/sys/net/ipv4/ip_forward
    iptables --table nat --append POSTROUTING --out-interface wlp4s0 -j MASQUERADE
    iptables --append FORWARD --in-interface wlp4s0 -j ACCEPT

About
======

.. image:: images/about.png
   :align: center
   :alt: about


BB-Config v2.x
***************

ADC (Graph)
============
- Plot graph for Analogue pin

.. image:: images/adc2.png
   :align: center
   :alt: adc page


.. image:: images/adc.png
   :align: center
   :alt: adc graph


DAC (PWM)
==========
- Generate PWM waveform

.. image:: images/pwm.png
   :align: center
   :alt: pwm


uEnv
=====
- Enable/Disable boot configuration

.. image:: images/uEnv.png
   :align: center
   :alt: uEnv


services
=========
- Enable/Disable services startup at boot

.. image:: images/service.png
   :align: center
   :alt: service


PINMUX
=======
- Display PIN I/O detail
- Config PINMUX

Hardware Display
-----------------
.. image:: images/pinmux.png
   :align: center
   :alt: pinmux hardware


Pin Table References
--------------------
.. image:: images/pinmux2.png
   :align: center
   :alt: pinmux table references


Pin Config
--------------
.. image:: images/pinmux3.png
   :align: center
   :alt: pinmux config


Overlay (dts)
==============
- Enable/Disable Device Tree Overlay in Boot option
- Select dtbo file and automate update in uEnv.txt 

.. image:: images/overlay.png
   :align: center
   :alt: overlay


WiFi (D-Bus)
=============
- Connect to WiFi with wpa_supplicant
- Support for Debian 11

.. image:: images/wifi-dbus.png
   :align: center
   :alt: WiFi D-Bus