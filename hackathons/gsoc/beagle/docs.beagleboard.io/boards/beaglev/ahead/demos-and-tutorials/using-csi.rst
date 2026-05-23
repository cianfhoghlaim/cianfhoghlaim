.. important:: 
    This document is a work on progress.

.. _beaglev-ahead-csi:

Using CSI Cameras
#################

.. note:: 
    CSI support is only available in Yocto image for BeagleV Ahead, 
    to flash latest Yoctor image on your BeagleV Ahead you can checkout 
    :ref:`beaglev-ahead-flashing-emmc` section.


Hardware
*********

IMX219 camera modules has been tested to work well with BeagleV Ahead, some of them are listed below:

1. `Raspberry Pi Camera Board v2 - 8 Megapixels (Adafruit) <https://www.adafruit.com/product/3099>`_
2. `Raspberry Pi NoIR Camera Board v2 - 8 Megapixels (Adafuit) <https://www.adafruit.com/product/3100>`_
3. `Arducam IMX219 (Robu.in) <https://robu.in/product/arducam-imx219-visible-light-fixed-focus-camera-module-for-raspberry-pi/>`_

In addition to the camer you'll need a 15pin to 22pin cable as well:

1. `Raspberry Pi Zero FPC Camera Cable (Adafruit) <https://www.adafruit.com/product/5211>`_
2. `Raspberry Pi Zero v1.3 Camera Cable (Adafuit) <https://www.adafruit.com/product/3157>`_
3. `Raspberry Pi Zero V1.3 Camera Cable (Robu.in) <https://robu.in/product/raspberry-pi-zero-v1-3-camera-cable/>`_

Software
*********

There are several demo applications available for testing CSI, execute commands 
below to test your IMX219 camera on CSI0 & CSI1 ports:

1. Change directory to demo application location using: ``cd /usr/share/vi/isp/test``
2. Set environment variable ``export ISP_LOG_LEVEL=3``
3. To test CSI0 execute: ``./camera_demo1 2 0 1 0 1920 1080 1 30 7``
4. To test CSI1 execute: ``./camera_demo1 0 0 1 0 1920 1080 1 30 7``

When you execure `camera_demo1` then you should see something like this on your console:

.. code-block:: bash

    ...
    ...
    IMX219: IMX219_IsiExposureControlIss: g=168.960999, Ti=0.050000
    CAMERIC-MI-IRQ: isp mi frame out (59)  fps[0]: 19.74
    IMX219: IMX219_IsiExposureControlIss: g=168.960999, Ti=0.050000
    CAMERIC-MI-IRQ: isp mi frame out (60)  fps[0]: 19.73
    IMX219: IMX219_IsiExposureControlIss: g=168.960999, Ti=0.050000
    CAMERIC-MI-IRQ: isp mi frame out (61)  fps[0]: 19.72
    IMX219: IMX219_IsiExposureControlIss: g=168.960999, Ti=0.050000
    CAMERIC-MI-IRQ: isp mi frame out (62)  fps[0]: 19.72
    IMX219: IMX219_IsiExposureControlIss: g=168.960999, Ti=0.050000
    CAMERIC-MI-IRQ: isp mi frame out (63)  fps[0]: 19.71
    ...
    ...

The output above indicates your CSI camera is working well. 

.. important::
    Usage of other demo applications will be added to this page as well.

Source for these demo application can be found 
`here <https://github.com/thead-yocto-mirror/csi_hal/tree/master/examples/camera>`_

