.. _beaglebone-blue-wifi:

WiFi Setup
#############

On my network, I’m set up as ip 192.168.1.*. To turn your wifi on, do the following.

.. code:: bash

   sudo -s
   (become superuser/root)
   cd /etc/network/
   ifconfig
   (Note the wifi inet address, if it is already set, you are done!)
   connmanctl
   tether wifi off
   enable wifi
   scan wifi
   services
   (at this point you should see your network appear along with other stuff, in my case it was "AR Crystal wifi_f45eab2f1ee1_6372797774616c_managed_psk")
   nano interfaces
   (or whatever editor you like)
   remove the comment # from the wifi lines so it now appears like
   ##connman: WiFi
   #
   connmanctl
   connmanctl> tether wifi off
   connmanctl> enable wifi
   connmanctl> scan wifi
   connmanctl> services
   connmanctl> agent on
   connmanctl> connect wifi_f45eab2f1ee1_6372797774616c_managed_psk
   connmanctl> quit
   exit
   note that you will need to fill in your own network data
