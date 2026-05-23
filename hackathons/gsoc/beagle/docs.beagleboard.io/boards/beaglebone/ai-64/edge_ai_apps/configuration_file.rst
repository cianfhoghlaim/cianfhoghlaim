.. _ai_64_edgeai_configuration:

Demo Configuration file
#########################

The demo config file uses YAML format to define input sources, models, outputs
and finally the flows which defines how everything is connected. Config files
for out-of-box demos are kept in ``edge_ai_apps/configs`` folder. The
folder contains config files for all the use cases and also multi-input and
multi-inference case. The folder also has a template YAML file
``app_config_template.yaml`` which has detailed explanation of all the
parameters supported in the config file.

Config file is divided in 4 sections:

#. Inputs
#. Models
#. Outputs
#. Flows

Inputs
======

The input section defines a list of supported inputs like camera, filesrc etc.
Their properties like shown below.

.. code-block:: yaml

    inputs:
        input0:                                         #Camera Input
            source: /dev/video2                         #Device file entry of the camera
            format: jpeg                                #Input data format supported by camera
            width: 1280                                 #Width and Height of the input
            height: 720
            framerate: 30                               #Framerate of the source

        input1:                                         #Video Input
            source: ../data/videos/video_0000_h264.mp4  #Video file
            format: h264                                #File encoding format
            width: 1280
            height: 720
            framerate: 25

        input2:                                         #Image Input
            source: ../data/images/%04d.jpg             #Sequence of Image files, printf style formatting is used
            width: 1280
            height: 720
            index: 0                                    #Starting Index (optional)
            framerate: 1

All supported inputs are listed in template config file.
Below are the details of most commonly used inputs.

.. _ai_64_edgeai_camera_sources:

Camera sources (v4l2)
---------------------

**v4l2src** GStreamer element is used to capture frames from camera sources
which are exposed as v4l2 devices. In Linux, there are many devices which are
implemented as v4l2 devices. Not all of them will be camera devices. You need
to make sure the correct device is configured for running the demo successfully.

``init_script.sh`` is ran as part of systemd, which detects all cameras connected
and prints the detail like below in the UART console:

.. code-block:: bash

   debian@beaglebone:/opt/edge_ai_apps# ./init_script.sh
   USB Camera detected
       device = /dev/video18
       format = jpeg
   CSI Camera 0 detected
       device = /dev/video2
       name = imx219 8-0010
       format = [fmt:SRGGB8_1X8/1920x1080]
       subdev_id = 2
       isp_required = yes
   IMX390 Camera 0 detected
       device = /dev/video18
       name = imx390 10-001a
       format = [fmt:SRGGB12_1X12/1936x1100 field: none]
       subdev_id = /dev/v4l-subdev7
       isp_required = yes
       ldc_required = yes

script can also be run manually later to get the camera details.

From the above log we can determine that 1 USB camera is connected
(/dev/video18), and 1 CSI camera is connected (/dev/video2) which is imx219 raw
sensor and needs ISP. IMX390 camera needs both ISP and LDC.

Using this method, you can configure correct device for camera capture in the
input section of config file.

.. code-block:: bash

    input0:
        source: /dev/video18  #USB Camera
        format: jpeg          #if connected USB camera supports jpeg
        width: 1280
        height: 720
        framerate: 30

    input1:
        source: /dev/video2  #CSI Camera
        format: auto         #let the gstreamer negotiate the format
        width: 1280
        height: 720
        framerate: 30

    input2:
        source: /dev/video2  #IMX219 raw sensor that needs ISP
        format: rggb         #ISP will be added in the pipeline
        width: 1920
        height: 1080
        framerate: 30
        subdev-id: 2         #needed by ISP to control sensor params via ioctls

    input3:
        source: /dev/video2  #IMX390 raw sensor that needs ISP
        width: 1936
        height: 1100
        format: rggb12       #ISP will be added in the pipeline
        subdev-id: 2         #needed by ISP to control sensor params via ioctls
        framerate: 30
        sen-id: imx390
        ldc: True            #LDC will be added in the pipeline

Make sure to configure correct ``format`` for camera input. ``jpeg`` for USB
camera that supports MJPEG (Ex. C270 logitech USB camera). ``auto`` for CSI
camera to allow gstreamer to negotiate the format. ``rggb`` for sensor
that needs ISP.

Video sources
-------------

H.264 and H.265 encoded videos can be provided as input sources to the demos.
Sample video files are provided under ``/opt/edge_ai_apps/data/videos/video_0000_h264.mp4``
and ``/opt/edge_ai_apps/data/videos/video_000_h265.mp4``

.. code-block:: yaml

    input1:
        source: ../data/videos/video_0000_h264.mp4
        format: h264
        width: 1280
        height: 720
        framerate: 25

    input2:
        source: ../data/videos/video_0000_h265.mp4
        format: h265
        width: 1280
        height: 720
        framerate: 25

Make sure to configure correct ``format`` for video input as shown above.
By default the format is set to ``auto`` which will then use the GStreamer
bin ``decodebin`` instead.

Image sources
-------------

JPEG compressed images can be provided as inputs to the demos. A sample set of
images are provided under ``/opt/edge_ai_apps/data/images``. The names of the
files are numbered sequentially and incrementally and the demo plays the files
at the fps specified by the user.

.. code-block:: yaml

    input2:
        source: ../data/images/%04d.jpg
        width: 1280
        height: 720
        index: 0
        framerate: 1

RTSP sources
------------

H.264 encoded video streams either coming from a RTSP compliant IP camera or
via RTSP server running on a remote PC can be provided as inputs to the demo.

.. code-block:: yaml

    input0:
        source: rtsp://172.24.145.220:8554/test # rtsp stream url, replace this with correct url
        width: 1280
        height: 720
        framerate: 30

.. note::

   Usually video streams from any IP camera will be encrypted and cannot be
   played back directly without a decryption key. We tested RTSP source by
   setting up an RTSP server on a Ubuntu 18.04 PC by referring to this writeup,
   `Setting up RTSP server on PC
   <https://gist.github.com/Santiago-vdk/80c378a315722a1b813ae5da1661f890>`_

Models
======

The model section defines a list of models that are used in the demo. Path to
the model directory is a required argument for each model and rest are optional
properties specific to given use cases like shown below.

.. code-block:: yaml

    models:
        model0:
            model_path: ../models/segmentation/ONR-SS-871-deeplabv3lite-mobv2-cocoseg21-512x512   #Model Directory
            alpha: 0.4                                                                            #alpha for blending segmentation mask (optional)
        model1:
            model_path: ../models/detection/TFL-OD-202-ssdLite-mobDet-DSP-coco-320x320
            viz_threshold: 0.3                                                                    #Visualization threshold for adding bounding boxes (optional)
        model2:
            model_path: ../models/classification/TVM-CL-338-mobileNetV2-qat
            topN: 5                                                                               #Number of top N classes (optional)

Below are some of the use case specific properties:

#. **alpha**: This determines the weight of the mask for blending the semantic
   segmentation output with the input image ``alpha * mask + (1 - alpha) * image``
#. **viz_threshold**: Score threshold to draw the bounding boxes for detected
   objects in object detection. This can be used to control the number of boxes
   in the output, increase if there are too many and decrease if there are very
   few
#. **topN**: Number of most probable classes to overlay on image classification
   output

The content of the model directory and its structure is discussed in detail in
:ref:`ai_64_edgeai_import_custom_models`


Outputs
=======

The output section defines a list of supported outputs.

.. code-block:: yaml

   outputs:
       output0:                                                     #Display Output
           sink: kmssink
           width: 1920                                              #Width and Height of the output
           height: 1080
           connector: 39                                            #Connector ID for kmssink (optional)

       output1:                                                     #Video Output
           sink: ../data/output/videos/output_video.mkv             #Output video file
           width: 1920
           height: 1080

       output2:                                                     #Image Output
           sink: ../data/output/images/output_image_%04d.jpg        #Image file name, printf style formatting is used
           width: 1920
           height: 1080

All supported outputs are listed in template config file.
Below are the details of most commonly used outputs

Display Sink (kmssink)
----------------------

When you have only one display connected to the SK, kmssink will try to use
it for displaying the output buffers. In case you have connected multiple
display monitors (e.g. Display Port and HDMI), you can select a specific display
for kmssink by passing a specific connector ID number.
Following command finds out the connected displays available to use.

**Note**: Run this command outside docker container. The first number in each
line is the connector-id which we will use in next step.

.. code-block:: bash

    debian@beaglebone:/opt/edge_ai_apps# modetest -M tidss -c | grep connected
    39      38      connected       DP-1            530x300         12      38
    48      0       disconnected    HDMI-A-1        0x0             0       47

From above output, we can see that connector ID 39 is connected. Configure the
connector ID in the output section of the config file.

Video sinks
-----------
The post-processed outputs can be encoded in H.264 format and stored on disk.
Please specify the location of the video file in the configuration file.

.. code-block:: yaml

    output1:
        sink: ../data/output/videos/output_video.mkv
        width: 1920
        height: 1080

Image sinks
-----------
The post-processed outputs can be stored as JPEG compressed images.
Please specify the location of the image files in the configuration file.
The images will be named sequentially and incrementally as shown.

.. code-block:: yaml

    output2:
        sink: ../data/output/images/output_image_%04d.jpg
        width: 1920
        height: 1080

Flows
=====

The flows section defines how inputs, models and outputs are connected.
Multiple flows can be defined to achieve multi input, multi inference like
below.

.. code-block:: yaml

    flows:
        flow0:                              #First Flow
            input: input0                   #Input for the Flow
            models: [model1, model2]        #List of models to be used
            outputs: [output0, output0]     #Outputs to be used for each model inference output
            mosaic:                         #Positions to place the inference outputs in the output frame
                mosaic0:
                    width:  800
                    height: 450
                    pos_x:  160
                    pos_y:  90
                mosaic1:
                    width:  800
                    height: 450
                    pos_x:  960
                    pos_y:  90
        flow1:                              #Second Flow
            input: input1
            models: [model0, model3]
            outputs: [output0, output0]
            mosaic:
                mosaic0:
                    width:  800
                    height: 450
                    pos_x:  160
                    pos_y:  540
                mosaic1:
                    width:  800
                    height: 450
                    pos_x:  960
                    pos_y:  540

Each flow should have exactly **1 input**, **n models** to infer the given input
and **n outputs** to render the output of each inference. Along with input, models
and outputs it is required to define **n mosaics** which are the position of the
inference output in the final output plane. This is needed because multiple
inference outputs can be rendered to same output (Ex: Display).

Command line arguments
----------------------

Limited set of command line arguments can be provided, run with '-h' or '--help'
option to list the supported parameters.

.. code-block:: bash

    usage: Run : ./app_edgeai.py -h for help

    positional arguments:
      config           Path to demo config file
                           ex: ./app_edgeai.py ../configs/app_config.yaml

    optional arguments:
      -h, --help       show this help message and exit
      -n, --no-curses  Disable curses report
                       default: Disabled
      -v, --verbose    Verbose option to print profile info on stdout
                       default: Disabled
