.. _beagleplay-demo-lpm-video:

Smart energy efficient video doorbell
#####################################

1. Intelligent camera streaming and recording at 640x480 resolution and 30 FPS with power saving.
2. Detect user activity using an external button/sensor and configure it as a wake-up source
3. Application should start streaming on wakeup event, pause on system suspend and resume back seamlessly thus saving power while system was in suspended state.

Give options to enable below functionalities:

- Stream Live camera feed when visitor activity is detected
- On-the-fly recording of live camera feed with a timeout to record visitor activity
- On-the-fly streaming of live camera feed to remote server for post processing/storage or display.

About deep sleep
******************

Deep Sleep AKA Suspend-to-RAM is a low-power mode that allows an embedded
device to retain its state in RAM while the processor is turned off.
This can save a significant amount of power, especially in devices that are battery-powered.

The benefits of using deep sleep in embedded devices are faster wake-up time and
better efficiency.

.. tip:: Checkout `kernel docs on power states <https://www.kernel.org/doc/Documentation/power/states.txt>`_

.. youtube:: 4jbOXl_o4uo
	:width: 100%
	:align: center

Hardware requirements
**********************

1. `BeaglePlay board <https://www.beagleboard.org/boards/beagleplay>`_
2. A CSI MIPI camera like `TEVI-OV5640 <https://www.technexion.com/products/embedded-vision/image-sensors/tevi-ov5640/>`_ or a USB web-cam
3. HDMI monitor & HDMI cable
4. Ethernet cable and a laptop/desktop with an Ethernet port
5. `A Grove PIR sensor <https://wiki.seeedstudio.com/Grove-PIR_Motion_Sensor/>`_ or a Grove button

Software requirements
*********************

First, make sure that you have the latest U-Boot which packages the right firmwares
to make deep sleep work on beagleplay. You will also need to use ti-linux-kernel for
basic suspend-to-RAM because the patches are yet to make it into upstream.

You can always use Robert Nelson's latest default debian images which should come with the
right uboot and kernel required.

On debian, you may also need to make sure you have gstreamer installed, refer to
https://gstreamer.freedesktop.org/documentation/installing/on-linux.html?gi-language=c
for further details on how to install gstreamer.

Devicetree changes
*******************

You will need to tell Linux what your wakeup source is going to be, it can be a simple button
or even a  PIR sensor. To do this you'll need to make the following changes to the
k3-am625-beagleplay.dts:

.. code:: diff

	diff --git a/arch/arm64/boot/dts/ti/k3-am625-beagleplay.dts b/arch/arm64/boot/dts/ti/k3-am625-beagleplay.dts
	index b3328ae24b5f..9a83102e3604 100644
	--- a/arch/arm64/boot/dts/ti/k3-am625-beagleplay.dts
	+++ b/arch/arm64/boot/dts/ti/k3-am625-beagleplay.dts
	@@ -166,6 +166,20 @@ vdd_sd_dv: regulator-5 {
				 <3300000 0x1>;
		};

	+	motion_gpio_key {
	+		compatible = "gpio-keys";
	+		autorepeat;
	+		pinctrl-names = "default";
	+		pinctrl-0 = <&grove_pins_default>;
	+		switch {
	+			label = "senseGPIO";
	+			linux,code = <KEY_WAKEUP>;
	+			interrupts-extended = <&main_gpio1 28 IRQ_TYPE_EDGE_RISING>,
	+				<&main_pmx0 0x1e8>;
	+			interrupt-names = "irq", "wakeup";
	+		};
	+	};
	+
		leds {
			compatible = "gpio-leds";

The above will help us configure the grove connector's GPIO to act as a
wakeup source from Deep Sleep.

If using the CSI MIPI camera like tevi-ov5640 then, be sure to also apply the respective overlay, 
for tevi-ov5640 apply ``k3-am625-beagleplay-csi2-tevi-ov5640.dtbo`` overlay.

The Technexion TEVI-OV5640 module supports Suspend-to-RAM but may fail to set the sensor registers
in time when built as a module. You can fix this by making it a part of the kernel image:
Find further details in the `TI-SDK Documentation <https://software-dl.ti.com/processor-sdk-linux/esd/AM62X/09_01_00_08/exports/docs/linux/Foundational_Components/Kernel/Kernel_Drivers/Camera/CSI2RX.html#suspend-to-ram>`_

.. todo:: Add the below changes to the beagle defconfig

.. code:: diff

	diff --git a/arch/arm64/configs/defconfig b/arch/arm64/configs/defconfig
	index 1f402994efed..0f081e5f96c1 100644
	--- a/arch/arm64/configs/defconfig
	+++ b/arch/arm64/configs/defconfig
	@@ -739,14 +739,14 @@ CONFIG_RC_DECODERS=y
	 CONFIG_RC_DEVICES=y
	 CONFIG_IR_MESON=m
	 CONFIG_IR_SUNXI=m
	-CONFIG_MEDIA_SUPPORT=m
	+CONFIG_MEDIA_SUPPORT=y
	 # CONFIG_DVB_NET is not set
	 CONFIG_MEDIA_USB_SUPPORT=y
	 CONFIG_USB_VIDEO_CLASS=m
	 CONFIG_V4L_PLATFORM_DRIVERS=y
	 CONFIG_SDR_PLATFORM_DRIVERS=y
	 CONFIG_V4L_MEM2MEM_DRIVERS=y
	-CONFIG_VIDEO_CADENCE_CSI2RX=m
	+CONFIG_VIDEO_CADENCE_CSI2RX=y
	 CONFIG_VIDEO_WAVE_VPU=m
	 CONFIG_VIDEO_IMG_VXD_DEC=m
	 CONFIG_VIDEO_IMG_VXE_ENC=m
	@@ -764,12 +764,12 @@ CONFIG_VIDEO_SAMSUNG_EXYNOS_GSC=m
	 CONFIG_VIDEO_SAMSUNG_S5P_JPEG=m
	 CONFIG_VIDEO_SAMSUNG_S5P_MFC=m
	 CONFIG_VIDEO_SUN6I_CSI=m
	-CONFIG_VIDEO_TI_J721E_CSI2RX=m
	+CONFIG_VIDEO_TI_J721E_CSI2RX=y
	 CONFIG_VIDEO_HANTRO=m
	 CONFIG_VIDEO_IMX219=m
	 CONFIG_VIDEO_IMX390=m
	 CONFIG_VIDEO_OV2312=m
	-CONFIG_VIDEO_OV5640=m
	+CONFIG_VIDEO_OV5640=y
	 CONFIG_VIDEO_OV5645=m
	 CONFIG_VIDEO_DS90UB953=m
	 CONFIG_VIDEO_DS90UB960=m
	@@ -1309,8 +1309,8 @@ CONFIG_PHY_XGENE=y
	 CONFIG_PHY_CAN_TRANSCEIVER=m
	 CONFIG_PHY_SUN4I_USB=y
	 CONFIG_PHY_CADENCE_TORRENT=y
	-CONFIG_PHY_CADENCE_DPHY=m
	-CONFIG_PHY_CADENCE_DPHY_RX=m
	+CONFIG_PHY_CADENCE_DPHY=y
	+CONFIG_PHY_CADENCE_DPHY_RX=y
	 CONFIG_PHY_CADENCE_SIERRA=y
	 CONFIG_PHY_MIXEL_MIPI_DPHY=m
	 CONFIG_PHY_FSL_IMX8M_PCIE=y

Linux commands
***************

Once your hardware, software and devicetree changes are all set, and
you boot till linux prompt we can finally start with the final bit. The below section describes various gstreamer pipelines created using sample gst-launch-1.0 gstreamer application. You can create your own gstreamer application too with some dynamic features, customized options taking referece from these pipelines.

.. note::
   If using CSI based TEVI-OV5640 module, you need to also set the mediagraph prior to using camera. You can set set the media graph and sanity test the camera using below command which uses cam tool from libcamera:

.. code:: console

	cam -c1 --stream width=640,height=480,pixelformat=UYVY -C20

Additionally, if using a different camera, you can check the supported resolutions and video formats using below command:

.. code:: console

	v4l2-ctl --all -d /dev/videoX (where X is your video node number e.g. /dev/video0)

There are two sets of gstreamer pipelines that get run in this demo one at server side i.e. on beagleplay board directly which captures and displays the camera feed and streams it to the remote or client side, and the other at client side itself which receives the camera feed, records it, decodes it and displays it using the remote host machine.

Server side gstreamer pipeline (on beagleplay board):
=====================================================

Here, you can run either of the below two sets of gstreamer pipeline depending upon your requirement :

Display live camera feed
------------------------

Pipeline topology
~~~~~~~~~~~~~~~~~

.. code:: console

	v4l2src --> kmssink

Gstreamer Pipeline
~~~~~~~~~~~~~~~~~~

.. code:: console

	#Stop weston if using kmssink
	systemctl stop weston.service
	gst-launch-1.0 -v v4l2src io-mode=dmabuf device="/dev/video0" ! video/x-raw, width=640, height=480, format=YUY2 ! kmssink 	driver-name=tidss force-modesetting=true sync=false async=false

.. note::
   Change the video format to UYVY if using CSI based ov5640 camera

Description
~~~~~~~~~~~~

The Linux kernel uses V4L2 based driver for Camera and DRM/KMS based driver for Display, Gstreamer has v4l2src element to communicate with V4l2's based driver and kmssink element to talk with display driver and using above command, we can create a media pipeline which shares video buffers from camera to display using DMA to transfer the buffer. This is specified using io-mode property of v4l2src.
By default display server i.e weston is in charge of controlling the display, so it needs to be disabled if we want to control the display directly. We also use kmssink's force-modesetting property to set the display mode to the camera resolution and have a full screen display. If using a graphics server involving GPU, one can use waylandsink (which uses weston as display server), glimagesink (which uses opengl API) or ximagesink (which uses Xorg as display server) depending upon the display server.

Display live camera feed + Stream out to remote server
------------------------------------------------------

Pipeline topology
~~~~~~~~~~~~~~~~~~

.. code:: console

                         .-->kmssink
	v4l2src --> tee--|
	                 .-->x264enc-->rtph264pay-->udpsink

Gstreamer pipeline
~~~~~~~~~~~~~~~~~~~

.. code:: console

	#Stop weston if using kmssink
	systemctl stop weston.service
	gst-launch-1.0 -v v4l2src io-mode=dmabuf device="/dev/video0" ! video/x-raw, width=640, height=480, format=YUY2 ! queue ! tee name=t t. ! queue ! kmssink driver-name=tidss force-modesetting=true sync=false async=false t. ! queue ! ticolorconvert ! queue ! x264enc speed-preset=superfast  key-int-max=30 tune=zerolatency bitrate=25000 ! queue ! rtph264pay config-interval=30 ! udpsink sync=false port=5000 host=192.168.0.2 async=false &

.. note::
   Change the video format to UYVY if using CSI based ov5640 camera

Description
~~~~~~~~~~~~

Here we use gstreamer's tee element to split the media pipeline graph into two arms, one arm is used to display the camera feed on-screen (which is same as the one described in previous section) and other arm is used to encode the camera feed and stream it to remote server. We use libx264 based x264enc element to encode the raw video to H.264 based access units. However x264enc does not support YUY2 video format, so we use ticolorconvert element to convert the video format to the one supported by the encoder, this element is CPU based but it uses ARM neon based instructions underneath for faster conversion. The x264enc element also offers different parameters to fine tune the encoding. We use superfast speed preset along with zerolatency tuning as we want to strem in realtime with minimal latency. We set IDR or key frame interval to 30 frames using key-int-max property. The IDR frame is important from streaming point of view as it marks arrival of fresh group of pictures without any dependencies to previous frames so that decoding at client side can resume back seamlessly even if there were packet losses in between due to network issues. However the value needs to be carefully chosen as the trade-off with higher frequency of IDR frames though is the increase in size of rtp payload which may consume more bandwidth. The video quality of encoded stream is controleld by bitrate parameter which specifies number of Kbits used for encoding video for 1s. Higher value for bitrate will increase the video quality albeit at the cost of increased size. The encoded frame is then packetized into RTP packets using rtph264pay element and transmitted over network using UDP protocol using udpsink element. The ip address and port number of remote host are specified using "host" and "port" property of udpsink element respectively.

This gstreamer pipeline is useful for prototyping use-case where you not just want to display the camera feed outside the door when some visitor comes, but also want to stream out to a remote server (for e.g. security control rool or to your mobile device) for more safety.

Display live camera feed + Stream out to remote server+ Record camera feed
--------------------------------------------------------------------------

Pipeline topology
~~~~~~~~~~~~~~~~~

.. code:: console

	                 .-->kmssink
	v4l2src --> tee--|                  .--filesink
	                 .-->x264enc-->tee--|
	                                    .--rtph264pay-->udpsink

Gstreamer pipeline
~~~~~~~~~~~~~~~~~~

.. code:: console

	#Stop weston if using kmssink
	systemctl stop weston.service
	gst-launch-1.0 -v v4l2src io-mode=dmabuf device="/dev/video0" ! video/x-raw, width=640, height=480, format=YUY2 ! queue ! tee name=t t. ! queue ! kmssink driver-name=tidss force-modesetting=true sync=false async=false t. ! queue ! ticolorconvert ! x264enc speed-preset=superfast key-int-max=30 bitrate=5000 ! queue ! tee name=t1 t1. ! queue ! rtph264pay config-interval=60 ! udpsink port=5000 host=192.168.0.2 sync=false async=false t1. ! queue ! filesink location="op.h264"

.. note::
   Change the video format to UYVY if using CSI based ov5640 camera

Description
~~~~~~~~~~~

In addition to the media topology described in previous section, one more tee element is added here to save the encoded file over user-specified storage media. This could be helpful to have the camera feed of all the visitors (or potential intruders :)) recorded at the device end itself for future reference/analysis or as a blackbox recording. However care needs to be taken to constantly backup the recorded stream so that storage media does not run out of space.

Client side gstreamer pipeline (runs on remote host):
=====================================================

The previous section described how the camera feed is displayed and streamed out to remote server using RTP and UDP protocols. Here we will discuss about how we can receive the transmitted stream and display it or record it. We use X86_64 based Ubuntu machine as remote host here.

Display camera feed received over network
------------------------------------------

Pipeline topology
~~~~~~~~~~~~~~~~~

.. code:: console

	udpsrc --> rtpjitterbuffer-->rtph264depay-->h264parse-->avdec_h264-->xvimagesink

Gstreamer pipeline
~~~~~~~~~~~~~~~~~~

.. code:: console

	# This is the IP address of the remote host which is specified in the server pipelien running on beagleplay
	sudo ifconfig enp2s0 192.168.0.2
	gst-launch-1.0 udpsrc port=5000 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtpjitterbuffer latency=50 ! rtph264depay ! h264parse ! avdec_h264 ! queue ! fpsdisplaysink text-overlay=false name=fpssink video-sink="xvimagesink sync=false" sync=false -v

Description
~~~~~~~~~~~~

The above gstreamer pipeline uses udpsrc element which reads UDP packets from the network, listening on the specified port (5000) and provide RTP packets to downstream element. rtpjitterbuffer element is used to buffer the incoming RTP packets to help reduce the impact of network jitter on smoothness of video. The bufferring is set to 50ms using latency property of rtpjitterbuffer, the value should be chosen optimally as tradeoff of choosing higher value is protection against network jitter maintaining the smoothness of pipeline but a higher value also increases the glass-to-glass latency. rtph264depay element is used to depacketize the H264 payload from RTP packets and feed send it to h264parse which parses it and provides access unit-by-access unit byte-stream to avdec_h264 which is a libav based software decoding element to decode H264 stream to raw video. fpsdisplaysink element is used along with xvimagesink (X11 backend) as video-sink to display overall frame-rate of the pipeline. If using weston as display server then waylandsink should be used as video-sink instead.

Display camera feed received over network + record incoming stream
------------------------------------------------------------------

Pipeline topology
~~~~~~~~~~~~~~~~~~

.. code:: console

	                                                             .-->avdec_h264-->xvimagesink
	udpsrc --> rtpjitterbuffer-->rtph264depay-->h264parse-->tee--|
                                                                     .-->filesink

Gstreamer pipeline
~~~~~~~~~~~~~~~~~~~

.. code:: console

	# This is the IP address of the remote host which is specified in the server pipelien running on beagleplay
	sudo ifconfig enp2s0 192.168.0.2
	gst-launch-1.0 udpsrc port=5000 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtpjitterbuffer latency=50 ! rtph264depay ! h264parse ! video/x-h264, stream-format=byte-stream ! tee name=t t. ! queue ! filesink location="op.h264"  t. ! queue ! avdec_h264 ! queue ! fpsdisplaysink text-overlay=false name=fpssink video-sink="xvimagesink sync=false" sync=false -v

Description
~~~~~~~~~~~~

This is same as pipeline described in previous section albeit with the extra addition of tee element which adds another arm to save the decoded video over a file on the host machine.

2. Let the above pipelines run in the background and then to suspend the device (beagleplay):

.. code:: console

	echo mem > /sys/power/state

3. Then, if you press the button/ trigger PIR sensor with some movement it should
   bring the device back up and you will see the video resume almost instantly on both the server side and client side. This is because underlying software stack also involving video and display related drivers support system suspend/resume, thus helping the application to resume seamlessly.

4. Additionally, you can enable auto suspend for the device by using a simple systemd service. Follow the `guide here <https://tecadmin.net/run-shell-script-as-systemd-service/>`_
   to see how to create and enable a script as a systemd service. The script that I used was as follows:

.. code:: console

        #!/bin/bash

        while true
        do
         sleep 15       # Adjust this time to whatever delay you prefer the device stays on after resume
         echo "Entering Suspend to RAM..."
         echo mem > /sys/power/state
        done

Resources
**********

1. https://software-dl.ti.com/processor-sdk-linux/esd/AM62X/09_02_01_09/exports/docs/linux/Foundational_Components/Kernel/Kernel_Drivers/Power_Management/pm_low_power_modes.html#deep-sleep
2. https://software-dl.ti.com/processor-sdk-linux/esd/AM62X/09_02_01_09/exports/docs/linux/Foundational_Components/Kernel/Kernel_Drivers/Camera/CSI2RX.html
