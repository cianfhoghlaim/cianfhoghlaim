.. _beaglebone-blue-ip-settings:

IP settings
############

You will usually want to have a fixed ip if you are doing robotics, so
you have a standard ip to connect to. If you are already connected in
dhcp you can borrow some of the settings from that to use in your new
configurations.

.. code:: bash

   route  

make a note of the default one, (in the example below 192.168.1.1)

.. code:: bash

   cat /etc/resolv.conf

make a note of the nameserver, (in the example below 8.8.8.8)

In my case I wanted 192.168.1.7 to do this,

.. code:: bash

   sudo -s
   connmanctl config wifi_f45eab2f1ee1_6372797774616c_managed_psk --ipv4 manual 192.168.1.7 255.255.255.0 192.168.1.1 --nameservers 8.8.8.8
   exit

the –ipv4 says to use ipv4 settings (as opposed to ipv6), the manual
means we are setting the values. 192.168.1.7 is the ip address we want.
(use your own of course). 255.255.255.0 is the network mask 192.168.1.1
is the route to the internet. (You’re might be different, but this is
common). –nameservers 8.8.8.8 says where to find the ip address for a
given domain name. the 8.8.8.8 says use’s googles
