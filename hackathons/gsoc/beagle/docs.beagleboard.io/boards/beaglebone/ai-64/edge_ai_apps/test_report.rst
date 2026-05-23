.. _ai_64_edgeai_test_report:

Test Report
############

Here is the summary of the sanity tests we ran with both Python and C++ demos.
Test cases vary with different inputs, outputs, runtime, models, python/c++ apps.

1. Inputs:

    * Camera (Logitech C270, 1280x720, JPEG)
    * Camera (Omnivision OV5640, 1280x720, YUV)
    * Camera (Rpi v2 Sony IMX219, 1920x1080, RAW)
    * Image files (30 images under edge_ai_apps/data/images)
    * Video file (10s video 1 file under edge_ai_apps/data/videos)
    * RSTP Video Server

2. Outputs:

    * Display (eDP or HDMI)
    * File write to SD card

3. Inference Type:

    * Image classification
    * Object detection
    * Semantic segmentation

4. Runtime/models:

    * DLR
    * TFLite
    * ONNX

5. Applications:

    * Python
    * C++

6. Platform:

   * Host OS
   * Docker


Demo Apps test report
=====================

Single Input Single Output
--------------------------

.. csv-table::
        :header: "Category", "# test case", "Pass", "Fail"

        Host OS - Python,99,99,0
        Host OS - C++,99,99,0

.. csv-table::
        :header: "S.No", "Models", "Input", "Output", "Host OS-C++", "Host OS-Python", "Docker-C++", "Docker-Python", "Comments"

	1,TVM-CL-3410-gluoncv-mxnet-mobv2,Image,Display,Pass,Pass,Pass,Pass
	2,TVM-CL-3410-gluoncv-mxnet-mobv2,Image,Video-Filewrite,Fail,Fail,Fail,Fail
	3,TVM-CL-3410-gluoncv-mxnet-mobv2,Image,Image-Filewrite,Pass,Pass,Pass,Pass
	4,TVM-CL-3410-gluoncv-mxnet-mobv2,Video,Display,Pass,Pass,Pass,Pass
	5,TVM-CL-3410-gluoncv-mxnet-mobv2,Video,Video-Filewrite,Pass,Pass,Pass,Pass
	6,TVM-CL-3410-gluoncv-mxnet-mobv2,USB Camera,Display,Pass,Pass,Pass,Pass
	7,TVM-CL-3410-gluoncv-mxnet-mobv2,USB Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	8,TVM-CL-3410-gluoncv-mxnet-mobv2,CSI Camera,Display,Pass,Pass,Pass,Pass
	9,TVM-CL-3410-gluoncv-mxnet-mobv2,CSI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	10,TVM-CL-3410-gluoncv-mxnet-mobv2,RPI Camera,Display,Pass,Pass,Pass,Pass
	11,TVM-CL-3410-gluoncv-mxnet-mobv2,RPI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	12,TVM-CL-3410-gluoncv-mxnet-mobv2,RTSP - Video,Display,Pass,Pass,Pass,Pass
	13,TVM-CL-3410-gluoncv-mxnet-mobv2,RTSP - Video,Video-Filewrite,Pass,Pass,Pass,Pass
	14,TFL-CL-0000-mobileNetV1-mlperf,Image,Display,Pass,Pass,Pass,Pass
	15,TFL-CL-0000-mobileNetV1-mlperf,Image,Video-Filewrite,Fail,Fail,Fail,Fail
	16,TFL-CL-0000-mobileNetV1-mlperf,Image,Image-Filewrite,Pass,Pass,Pass,Pass
	17,TFL-CL-0000-mobileNetV1-mlperf,Video,Display,Pass,Pass,Pass,Pass
	18,TFL-CL-0000-mobileNetV1-mlperf,Video,Video-Filewrite,Pass,Pass,Pass,Pass
	19,TFL-CL-0000-mobileNetV1-mlperf,USB Camera,Display,Pass,Pass,Pass,Pass
	20,TFL-CL-0000-mobileNetV1-mlperf,USB Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	21,TFL-CL-0000-mobileNetV1-mlperf,CSI Camera,Display,Pass,Pass,Pass,Pass
	22,TFL-CL-0000-mobileNetV1-mlperf,CSI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	23,TFL-CL-0000-mobileNetV1-mlperf,RPI Camera,Display,Pass,Pass,Pass,Pass
	24,TFL-CL-0000-mobileNetV1-mlperf,RPI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	25,TFL-CL-0000-mobileNetV1-mlperf,RTSP - Video,Display,Pass,Pass,Pass,Pass
	26,TFL-CL-0000-mobileNetV1-mlperf,RTSP - Video,Video-Filewrite,Pass,Pass,Pass,Pass
	27,ONR-CL-6360-regNetx-200mf,Image,Display,Pass,Pass,Pass,Pass
	28,ONR-CL-6360-regNetx-200mf,Image,Video-Filewrite,Fail,Fail,Fail,Fail
	29,ONR-CL-6360-regNetx-200mf,Image,Image-Filewrite,Pass,Pass,Pass,Pass
	30,ONR-CL-6360-regNetx-200mf,Video,Display,Pass,Pass,Pass,Pass
	31,ONR-CL-6360-regNetx-200mf,Video,Video-Filewrite,Pass,Pass,Pass,Pass
	32,ONR-CL-6360-regNetx-200mf,USB Camera,Display,Pass,Pass,Pass,Pass
	33,ONR-CL-6360-regNetx-200mf,USB Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	34,ONR-CL-6360-regNetx-200mf,CSI Camera,Display,Pass,Pass,Pass,Pass
	35,ONR-CL-6360-regNetx-200mf,CSI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	36,ONR-CL-6360-regNetx-200mf,RPI Camera,Display,Pass,Pass,Pass,Pass
	37,ONR-CL-6360-regNetx-200mf,RPI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	38,ONR-CL-6360-regNetx-200mf,RTSP - Video,Display,Pass,Pass,Pass,Pass
	39,ONR-CL-6360-regNetx-200mf,RTSP - Video,Video-Filewrite,Pass,Pass,Pass,Pass
	40,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,Image,Display,Pass,Pass,Pass,Pass
	41,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,Image,Video-Filewrite,Fail,Fail,Fail,Fail
	42,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,Image,Image-Filewrite,Pass,Pass,Pass,Pass
	43,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,Video,Display,Pass,Pass,Pass,Pass
	44,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,Video,Video-Filewrite,Pass,Pass,Pass,Pass
	45,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,USB Camera,Display,Pass,Pass,Pass,Pass
	46,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,USB Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	47,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,CSI Camera,Display,Pass,Pass,Pass,Pass
	48,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,CSI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	49,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,RPI Camera,Display,Pass,Pass,Pass,Pass
	50,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,RPI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	51,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,RTSP - Video,Display,Pass,Pass,Pass,Pass
	52,TVM-OD-5020-yolov3-mobv1-gluon-mxnet-coco-416x416,RTSP - Video,Video-Filewrite,Pass,Pass,Pass,Pass
	53,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,Image,Display,Pass,Pass,Pass,Pass
	54,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,Image,Video-Filewrite,Fail,Fail,Fail,Fail
	55,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,Image,Image-Filewrite,Pass,Pass,Pass,Pass
	56,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,Video,Display,Pass,Pass,Pass,Pass
	57,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,Video,Video-Filewrite,Pass,Pass,Pass,Pass
	58,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,USB Camera,Display,Pass,Pass,Pass,Pass
	59,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,USB Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	60,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,CSI Camera,Display,Pass,Pass,Pass,Pass
	61,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,CSI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	62,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,RPI Camera,Display,Pass,Pass,Pass,Pass
	63,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,RPI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	64,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,RTSP - Video,Display,Pass,Pass,Pass,Pass
	65,TFL-OD-2020-ssdLite-mobDet-DSP-coco-320x320,RTSP - Video,Video-Filewrite,Pass,Pass,Pass,Pass
	66,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,Image,Display,Pass,Pass,Pass,Pass
	67,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,Image,Video-Filewrite,Fail,Fail,Fail,Fail
	68,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,Image,Image-Filewrite,Pass,Pass,Pass,Pass
	69,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,Video,Display,Pass,Pass,Pass,Pass
	70,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,Video,Video-Filewrite,Pass,Pass,Pass,Pass
	71,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,USB Camera,Display,Pass,Pass,Pass,Pass
	72,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,USB Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	73,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,CSI Camera,Display,Pass,Pass,Pass,Pass
	74,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,CSI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	75,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,RPI Camera,Display,Pass,Pass,Pass,Pass
	76,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,RPI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	77,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,RTSP - Video,Display,Pass,Pass,Pass,Pass
	78,ONR-OD-8050-ssd-lite-regNetX-800mf-fpn-bgr-mmdet-coco-512x512,RTSP - Video,Video-Filewrite,Pass,Pass,Pass,Pass
	79,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,Image,Display,Pass,Pass,Pass,Pass
	80,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,Image,Video-Filewrite,Fail,Fail,Fail,Fail
	81,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,Image,Image-Filewrite,Pass,Pass,Pass,Pass
	82,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,Video,Display,Pass,Pass,Pass,Pass
	83,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,Video,Video-Filewrite,Pass,Pass,Pass,Pass
	84,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,USB Camera,Display,Pass,Pass,Pass,Pass
	85,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,USB Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	86,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,CSI Camera,Display,Pass,Pass,Pass,Pass
	87,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,CSI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	88,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,RPI Camera,Display,Pass,Pass,Pass,Pass
	89,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,RPI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	90,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,RTSP - Video,Display,Pass,Pass,Pass,Pass
	91,TVM-SS-5720-deeplabv3lite-regnetx800mf-cocoseg21-512x512,RTSP - Video,Video-Filewrite,Pass,Pass,Pass,Pass
	92,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,Image,Display,Pass,Pass,Pass,Pass
	93,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,Image,Video-Filewrite,Fail,Fail,Fail,Fail
	94,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,Image,Image-Filewrite,Pass,Pass,Pass,Pass
	95,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,Video,Display,Pass,Pass,Pass,Pass
	96,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,Video,Video-Filewrite,Pass,Pass,Pass,Pass
	97,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,USB Camera,Display,Pass,Pass,Pass,Pass
	98,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,USB Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	99,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,CSI Camera,Display,Pass,Pass,Pass,Pass
	100,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,CSI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	101,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,RPI Camera,Display,Pass,Pass,Pass,Pass
	102,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,RPI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	103,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,RTSP - Video,Display,Pass,Pass,Pass,Pass
	104,TFL-SS-2580-deeplabv3_mobv2-ade20k32-mlperf-512x512,RTSP - Video,Video-Filewrite,Pass,Pass,Pass,Pass
	105,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,Image,Display,Pass,Pass,Pass,Pass
	106,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,Image,Video-Filewrite,Fail,Fail,Fail,Fail
	107,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,Image,Image-Filewrite,Pass,Pass,Pass,Pass
	108,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,Video,Display,Pass,Pass,Pass,Pass
	109,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,Video,Video-Filewrite,Pass,Pass,Pass,Pass
	110,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,USB Camera,Display,Pass,Pass,Pass,Pass
	111,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,USB Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	112,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,CSI Camera,Display,Pass,Pass,Pass,Pass
	113,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,CSI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	114,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,RPI Camera,Display,Pass,Pass,Pass,Pass
	115,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,RPI Camera,Video-Filewrite,Pass,Pass,Pass,Pass
	116,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,RTSP - Video,Display,Pass,Pass,Pass,Pass
	117,ONR-SS-8610-deeplabv3lite-mobv2-ade20k32-512x512,RTSP - Video,Video-Filewrite,Pass,Pass,Pass,Pass


Single Input Multi Output
-------------------------
.. csv-table::
        :header: "Category", "# test case", "Pass", "Fail"

        Host OS - Python,15,15,0
        docker - Python,15,15,0
        Host OS - C++,15,15,0
        Docker - C++,15,15,0
.. csv-table::
        :header: "S.No", "Models", "Input", "Output", "Host OS-C++", "Host OS-Python", "Docker-C++", "Docker-Python", "Comments"

        1,"2 Models (TFL-CL, ONR-SS)",%04d.jpg,Display,Pass,Pass,Pass,Pass,
        2,"3-Models (TVM-CL, TFL-OD, ONR-SS)",%04d.jpg,Display,Pass,Pass,Pass,Pass,
        3,"4-Models (TVM-SS, TFL-OD, ONR-SS, ONR-CL)",%04d.jpg,Display,Pass,Pass,Pass,Pass,
        4,"2 Models (TFL-CL, ONR-SS)",video_0000.mp4,Display,Pass,Pass,Pass,Pass,
        5,"3-Models (TVM-CL, TFL-OD, ONR-SS)",video_0000.mp4,Display,Pass,Pass,Pass,Pass,
        6,"4-Models (TVM-SS, TFL-OD, ONR-SS, ONR-CL)",video_0000.mp4,Display,Pass,Pass,Pass,Pass,
        7,"2 Models (TFL-CL, ONR-SS)",USB_camera,Display,Pass,Pass,Pass,Pass,
        8,"3-Models (TVM-CL, TFL-OD, ONR-SS)",USB_camera,Display,Pass,Pass,Pass,Pass,
        9,"4-Models (TVM-SS, TFL-OD, ONR-SS, ONR-CL)",USB_camera,Display,Pass,Pass,Pass,Pass,
        10,"2 Models (TFL-CL, ONR-SS)",CSI_camera,Display,Pass,Pass,Pass,Pass,
        11,"3-Models (TVM-CL, TFL-OD, ONR-SS)",CSI_camera,Display,Pass,Pass,Pass,Pass,
        12,"4-Models (TVM-SS, TFL-OD, ONR-SS, ONR-CL)",CSI_camera,Display,Pass,Pass,Pass,Pass,
        13,"2 Models (TFL-CL, ONR-SS)",rtsp,Display,Pass,Pass,Pass,Pass,
        14,"3-Models (TVM-CL, TFL-OD, ONR-SS)",rtsp,Display,Pass,Pass,Pass,Pass,
        15,"4-Models (TVM-SS, TFL-OD, ONR-SS, ONR-CL)",rtsp,Display,Pass,Pass,Pass,Pass,

Multi Input Multi Output
------------------------
.. csv-table::
        :header: "Category", "# test case", "Pass", "Fail"

        Host OS - Python,8,8,0
        docker - Python,8,8,0
        Host OS - C++,8,8,0
        Docker - C++,8,8,0
.. csv-table::
        :header: "S.No", "Models", "Input", "Output", "Host OS-C++", "Host OS-Python", "Docker-C++", "Docker-Python", "Comments"

        1,"2 Models (TVM-CL, TFL-OD)","%04d.jpg,video_0000.mp4",Display,Pass,Pass,Pass,Pass,
        2,"2 Models (TVM-OD, ONR-SS)","%04d.jpg,rtsp",Video-Filewrite,Pass,Pass,Pass,Pass,
        3,"2 Models (ONR-CL, TVM-SS)","%04d.jpg,USB_camera",Display,Pass,Pass,Pass,Pass,
        4,"3-Models (TVM-CL, TFL-OD, ONR-SS)","%04d.jpg,CSI_camera,rtsp",Video-Filewrite,Pass,Pass,Pass,Pass,
        5,"3-Models (TVM-CL, TFL-OD, ONR-SS)","video_0000.mp4,rtsp,%04d.jpg",Display,Pass,Pass,Pass,Pass,
        6,"3-Models (TFL-CL, ONR-CL, TVM-SS)","video_0000.mp4,USB_camera,CSI_camera",Video-Filewrite,Pass,Pass,Pass,Pass,
        7,"4-Models (TVM-CL, TFL-SS, ONR-OD, TFL-CL)","USB_camera,CSI_camera",Display,Pass,Pass,Pass,Pass,
        8,"4-Models (TVM-SS, TFL-SS, ONR-SS, ONR-OD)","USB_camera,video_0000.mp4",Video-Filewrite,Pass,Pass,Pass,Pass,

.. note::
    * Video file from RTSP server used for RTSP input test
    * Please refer to the `TI Edge AI SDK release notes and known issues <https://software-dl.ti.com/jacinto7/esd/edgeai-sdk-j721e/latest/exports/docs/release_notes.html>`__ for more details
