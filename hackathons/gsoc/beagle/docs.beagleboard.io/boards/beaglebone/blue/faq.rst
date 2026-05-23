.. _beaglebone-blue-faq:

Frequently Asked Questions (FAQs)
#################################

.. important:: 
      All support for BeagleBone Blue design is through BeagleBoard.org community 
      at `BeagleBoard.org forum <https://forum.beagleboard.org/tag/beaglebone-blue>`_.

Production board boot media
****************************

.. todo:: Add production boot media link in ``_static/epilog/production.image`` and reference it here.

.. _are_there_any_books_to_help_me_get_started:

Are there any books to help me get started?
********************************************

The book `BeagleBone Robotic Projects, Second
Edition <https://github.com/jadonk/BeagleBone-Robotic-Projects-Second-Edition>`__
specifically covers how to get started building robots with BeagleBone
Blue.

For more general books on BeagleBone, Linux and other related topics,
see https://beagleboard.org/books.

.. _what_system_firmware_should_i_use_for_starting_to_explore_my_beaglebone_blue:

What system firmware should I use for starting to explore my BeagleBone Blue?
*******************************************************************************

Download the latest 'IoT' image from
https://www.beagleboard.org/distros. As of this writing, that image is
https://debian.beagleboard.org/images/bone-debian-9.5-iot-armhf-2018-10-07-4gb.img.xz.

Use http://etcher.io for writing that image to a 4GB or larger microSD
card.

Power-up your BeagleBone Blue with the newly created microSD card to run
this firmware image.

.. _what_is_the_name_of_the_access_point_ssid_and_password_default_on_beaglebone_blue:

What is the name of the access point SSID and password default on BeagleBone Blue?
*************************************************************************************

| SSID: BeagleBone-XXXX where XXXX is based upon the board's assigned
  unique hardware address
| Password: BeagleBone

.. _ive_connected_to_beaglebone_blues_access_point._how_do_i_get_logged_into_the_board:

I've connected to BeagleBone Blue's access point. How do I get logged into the board?
**************************************************************************************

Browse to http://192.168.8.1:3000 to open the Visual Studio Code IDE and get access
to the Linux command prompt.

If you've connected via USB instead, the address will be either
http://192.168.6.2:3000 or http://192.168.7.2:3000, depending on the USB
networking drivers provided by your operating system.

.. _how_do_i_connect_beaglebone_blue_to_my_own_wifi_network:

How do I connect BeagleBone Blue to my own WiFi network?
*********************************************************

From the bash command prompt in Linux:

.. code:: bash

   sudo -s (become superuser/root)

   connmanctl
      connmanctl> tether wifi off (not really necessary on latest images)
      connmanctl> enable wifi (not really necessary)
      connmanctl> scan wifi
      connmanctl> services (at this point you should see your network
      appear along with other stuff, in my case it was "AR Crystal wifi_f45eab2f1ee1_6372797774616c_managed_psk")
      connmanctl> agent on
      connmanctl> connect wifi_f45eab2f1ee1_6372797774616c_managed_psk
      connmanctl> quit

.. _where_can_i_find_examples_and_apis_for_programming_beaglebone_blue:

Where can I find examples and APIs for programming BeagleBone Blue?
********************************************************************

Programming in C: http://www.strawsondesign.com/#!manual-install

Programming in Python: https://github.com/mcdeoliveira/rcpy

Programming in Simulink:
https://www.mathworks.com/hardware-support/beaglebone-blue.html

.. _my_beaglebone_blue_fails_to_run_successful_tests:

My BeagleBone Blue fails to run successful tests
***************************************************

You've tried to run rc_test_drivers to ensure your board is working for
DOA warranty tests, but it errors. You should first look to fixing your
bootloader as described
http://strawsondesign.com/docs/librobotcontrol/installation.html#installation_s5

.. _im_running_an_image_off_of_a_microsd_card._how_do_i_write_it_to_the_on_board_emmc_flash:

I'm running an image off of a microSD card. How do I write it to the on-board eMMC flash?
*****************************************************************************************

Refer to the "Flashing Firmware" page:
https://git.beagleboard.org/beagleboard/beaglebone-blue/-/wikis/Flashing-firmware

Meanwhile, as root, run the
/opt/scripts/tools/eMMC/bbb-eMMC-flasher-eewiki-ext4.sh script which
will create a copy of the system in your microSD to a new single ext4
partition on the on-board eMMC.

.. _ive_written_the_latest_image_to_a_usd_card_but_some_features_arent_working._how_do_i_make_it_run_properly:

I’ve written the latest image to a uSD card, but some features aren’t working. How do I make it run properly?
***************************************************************************************************************

It is possible you are running an old bootloader off of the eMMC. While
power is completely off, hold the SD button (near the servo headers)
while applying power. You can release the button as soon the power LED
comes on. This will make sure the bootloader is loaded from microSD and
not eMMC.

Verify the running image using
`version.sh <https://github.com/RobertCNelson/boot-scripts/blob/master/tools/version.sh>`__
via:

.. code:: bash

   sudo /opt/scripts/tools/version.sh

The version.sh output will tell you which version of bootloader is on
the eMMC or microSD. Future versions of version.sh might further inform
you `if the SD button was properly asserted on
power-up <https://github.com/RobertCNelson/boot-scripts/issues/93>`__.

One you’ve booted the latest image, you can update the bootloader on the
eMMC using
`/opt/scripts/tools/developers/update_bootloader.sh <https://github.com/RobertCNelson/boot-scripts/blob/master/tools/developers/update_bootloader.sh>`__.
Better yet, read the `above
FAQ <https://git.beagleboard.org/beagleboard/beaglebone-blue/-/wikis/Frequently-Asked-Questions-(FAQ)#Im_running_an_image_off_of_a_microSD_card_How_do_I_write_it_to_the_onboard_eMMC_flash>`__
on flashing firmware.

.. _ive_got_my_on_board_emmc_flash_configured_in_a_nice_way._how_do_i_copy_that_to_other_beaglebone_blue_boards:

I've got my on-board eMMC flash configured in a nice way. How do I copy that to other BeagleBone Blue boards?
***************************************************************************************************************

As root, run the
`/opt/scripts/tools/eMMC/beaglebone-black-make-microSD-flasher-from-eMMC.sh <https://github.com/RobertCNelson/boot-scripts/blob/master/tools/eMMC/beaglebone-black-make-microSD-flasher-from-eMMC.sh>`__
script with a blank 4GB or larger microSD card installed and wait for
the script to complete execution.

Remove the microSD card.

Boot your other BeagleBone Blue boards off of this newly updated microSD
card and wait for the flashing process to complete. You'll know it
successfully started when you see the "larson scanner" running on the
LEDs. You'll know it successfully completed when it shuts off the board.

Remove the microSD card.

Reboot your newly flashed board.

.. _i_have_some_low_latency_io_tasks._how_do_i_get_started_programming_the_beaglebone_prus:

I have some low-latency I/O tasks. How do I get started programming the BeagleBone PRUs?
*****************************************************************************************

There is a "Hello, World" app at
https://gist.github.com/jadonk/2ecf864e1b3f250bad82c0eae12b7b64 that
will get you blinking the USRx LEDS.

The `libroboticscape
software <https://github.com/StrawsonDesign/Robotics_Cape_Installer>`__
provides examples that are pre-built and included in the BeagleBone Blue
software images for running the servo/ESC outputs and fourth quadrature
encoder input. You can use those firmware images as a basis for building
your own:
https://github.com/StrawsonDesign/Robotics_Cape_Installer/tree/master/pru_firmware

You can find some more at https://beagleboard.org/pru

.. _are_there_available_mechanical_models:

Are there available mechanical models?
****************************************

A community contributed model is available at
https://grabcad.com/library/beaglebone-blue-1

.. _what_is_the_operating_temperature_range:

What is the operating temperature range?
*****************************************

\`0..70\` due to processor, else \`-20..70\`

.. _what_is_the_dc_motor_drive_strength:

What is the DC motor drive strength?
*************************************

This is dictated by the 2 cell LiPo battery input, the `TB6612FNG motor
drivers <http://www.pololu.com/file/0J86/TB6612FNG.pdf>`__ and the
`JST-ZH connectors <http://www.jst-mfg.com/product/detail_e.php?series=287>`__

-  Voltage: 6V-8.4V (typical)
-  Current: 1A (maximum for connectors) / 1.2A (maximum average from
   drivers) / 3.2A (peak from drivers) per channel
