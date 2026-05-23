.. _beagleplay-rtc:

Using RTC
#########

BeaglePlay has an onboard Real Time Clock (BQ32002). If you have installed a CR1220 battery, you can use this to keep the time even when the device has been powered off, or has no Internet access to get time using ntp servers.

Understanding multiple rtc devices
***********************************

On the BeaglePlay there's 2 separate RTC devices. One is the inbuilt one - which by default shows up as ``/dev/rtc0``. And the other is BQ32002 - which is it's own discrete chip - and shows up as ``/dev/rtc1`` by default.

You can find out the time set in both these clocks with the ``hwclock`` command.

.. code:: shell-session
	  
   debian@BeaglePlay:~$ sudo hwclock -r --rtc /dev/rtc0
   2023-12-21 12:43:52.007564+05:30
   debian@BeaglePlay:~$ sudo hwclock -r --rtc /dev/rtc1
   1970-01-01 05:33:28.877722+05:30

Note that the time in ``rtc0`` has been set after booting up using ntp servers automatically.

Get the current time, timezone, and other settings
***************************************************

.. code:: shell-session
		
   debian@BeaglePlay:~$ timedatectl
	       Local time: Thu 2023-12-21 00:20:19 EST
	       Universal time: Thu 2023-12-21 05:20:19 UTC
	       RTC time: Thu 2023-12-21 05:20:20
	       Time zone: America/New_York (EST, -0500)
	       System clock synchronized: yes
	       NTP service: active
	       RTC in local TZ: no

The above command shows the time set on BeaglePlay, the universal time, the time set on the RTC, the timezone, and more. From the above we can see that the time in UTC is 5:20hrs and the time as per the timezone is 00:20hrs.

Setting the timezone
***********************

You can see the available timezones using the following command -

.. code:: shell-session

   debian@BeaglePlay:~$ timedatectl list-timezones

You can quit viewing the list by pressing the q character on your keyboard.

Once you have selected your timezone, you can set it as follows

.. code:: shell-session
	  
   debian@BeaglePlay:~$ sudo timedatectl set-timezone America/New_York


Enable ntp
************

We can set the time using ntp servers. This requires us to be connected to the Internet.

.. code:: shell-session
	  
   debian@BeaglePlay:~$ sudo timedatectl set-ntp true

Setting the time manually
***************************

You might want to set the time manually on your BeaglePlay. In this case you need to first disable the ntp synchronization.

.. code:: shell-session
	  
   debian@BeaglePlay:~$ sudo timedatectl set-ntp false
   debian@BeaglePlay:~$ sudo timedatectl set-time "2023-12-21 03:00:00"

Using the above command we have set the time to 0300hrs on 21st December 2023.

Using ``rtcwake`` to sleep
****************************

If you would like to put your BeaglePlay to sleep for a predetermined period of time, you can use the ``rtcwake`` command

.. code:: shell-session

   debian@BeaglePlay:~$ sudo sudo rtcwake -m disk --seconds 120 -d /dev/rtc1 -v
   Using UTC time.
        delta   = 0
        tzone   = 0
        tzname  = UTC
        systime = 1703147162, (UTC) Thu Dec 21 08:26:02 2023
        rtctime = 1703147162, (UTC) Thu Dec 21 08:26:02 2023
   alarm 0, sys_time 1703147162, rtc_time 1703147162, seconds 120
   rtcwake: wakeup from "disk" using /dev/rtc1 at Thu Dec 21 08:28:03 2023
   suspend mode: disk; suspending system
	  
The above command puts your BeaglePlay to sleep for 120 seconds, by writing the contents of your memory to disk. You can find what are the different modes that are supported similar to ``disk`` by running the ``--list-modes`` subcommand.

.. code:: shell-session

   debian@BeaglePlay:~$ rtcwake --list-modes
   freeze mem disk off no on disable show
