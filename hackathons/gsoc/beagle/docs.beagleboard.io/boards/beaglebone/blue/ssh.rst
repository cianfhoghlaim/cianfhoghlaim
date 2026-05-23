.. _beaglebone-blue-passowrd:

SSH 
####

If you don’t have ssh installed, install it. (google is your friend)
Then `ssh debian@192.168.7.2` The board will tell you what the password
is, on my it was `temppwd`.

To change your password use the command password it will ask you what your
current password is, then ask for the replacement. Then it will say it
was too simple and you have to do it again. Normal stuff.

If you want to insist on using your simple password, try this.

.. code:: bash

   sudo -s
   (become superuser/root)
   enter your password
   password debian
    (put your simple password in)
   exit
   (exit from superuser/root) 

When you are running as root, password is more compliant and will accept
simple password
