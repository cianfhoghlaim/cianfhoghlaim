.. _beagley-ai-using-imx219-csi-cameras:

Using IMX219 CSI Cameras
############################

.. todo:: Add further testing steps, results, and images.

.. todo:: Need to add `gstreamer` and/or `cheese` commands to show how to make use of connected cameras.

Camera connection
******************

You have to make sure the CSI camera FPC cable is connected in proper orientation for camera to work properly. 
The image below shows how it should look when connected correctly.

.. tip:: The image shows camera connection to ``CSI0`` port, you can similarly connect a camera to ``CSI1/DSI0`` port

.. figure:: ../images/camera/csi-camera-connection.*
   :align: center
   :alt: BeagleY-AI camera connection

   BeagleY-AI camera connection

Configuring CSI camera
***********************

To enable an IMX219 CSI camera, we have to modify the following file: ``/boot/firmware/extlinux/extlinux.conf``. We can check the available list of Device Tree Overlays using command below,

.. code:: console

   ls /boot/firmware/overlays/ | grep "beagley"

When executed the above command should give output show below,

.. code:: console

   debian@BeagleBone:~$ ls /boot/firmware/overlays/ | grep "beagley"
   k3-am67a-beagley-ai-csi0-imx219.dtbo
   k3-am67a-beagley-ai-csi0-ov5640.dtbo
   k3-am67a-beagley-ai-csi1-imx219.dtbo
   k3-am67a-beagley-ai-dsi-rpi-7inch-panel.dtbo
   k3-am67a-beagley-ai-lincolntech-185lcd-panel.dtbo

Using CSI Port 0
==================

Add the line shown below to ``/boot/firmware/extlinux/extlinux.conf`` 
file to load the IMX219 CSI0 device tree overlay: 

.. code:: bash

   fdtoverlays /overlays/k3-am67a-beagley-ai-csi0-imx219.dtbo

Your ``/boot/firmware/extlinux/extlinux.conf`` file should look something like this:

.. code:: bash

   label microSD (default)
      kernel /Image
      append console=ttyS2,115200n8 root=/dev/mmcblk0p2 ro rootfstype=ext4 rootwait net.ifnames=0
      fdtdir /
      fdt /ti/k3-am67a-beagley-ai.dtb
      fdtoverlays /overlays/k3-am67a-beagley-ai-csi0-imx219.dtbo
      initrd /initrd.img

Now reboot you BeagleY-AI to load the overlay,

.. code:: console

   sudo reboot

After ``reboot`` you can use ``beagle-camera-setup`` to setup your IMX219 CSI camera,

.. code:: console

   sudo beagle-camera-setup

``beagle-camera-setup`` should give you below output,

.. code:: console

   debian@beagle:~$ sudo beagle-camera-setup 
   [sudo] password for beagle: 
   IMX219 Camera 0 detected
      device = /dev/video-imx219-cam0
      name = imx219
      format = [fmt:SRGGB8_1X8/1920x1080]
      subdev_id = /dev/v4l-imx219-subdev0
      isp_required = yes

To check if the configuration is successfull you can check the video devices 
with ``ls /dev/ | grep video`` and you should see ``video-imx219-cam0`` listed as show below,

.. code:: console 

   beagle@beagle:~$ ls /dev/ | grep video
   video-imx219-cam0
   video0
   video1
   video2
   video3
   video4
   video5
   video6
   video7
   video8

Using CSI Port 1
*****************

.. todo:: add instructions to setup CSI1

Photos & video
***************

.. todo:: add instruction to take photos and videos

Troubleshooting
*******************

.. code:: console

   Found /extlinux/extlinux.conf
   Retrieving file: /extlinux/extlinux.conf
   beagley-ai microSD (extlinux.conf)
      1:      microSD Recovery
      2:      microSD (RPI 7inch panel)
      3:      microSD (lincolntech-185lcd panel)
      4:      microSD (csi0 imx219)
      5:      microSD (csi1 imx219)
      6:      microSD (csi0 ov5640)
      7:      microSD (default)
   Enter choice: 4
      4:      microSD (csi0 imx219)
