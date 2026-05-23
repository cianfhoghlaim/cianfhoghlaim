.. _bbai64-support:

Additional Support Information
##############################

All support for this design is through BeagleBoard.org community 
at `BeagleBoard.org forum <https://forum.beagleboard.org/tag/bbai64>`_.

.. _bbai64-certifications:

Certifications and export control
*********************************

Export designations
===================

* HS: 8471504090
* US HS: 8543708800
* EU HS: 8471707000

.. _hardware-design:

Hardware Design
****************

You can find all BeagleBone AI-64 hardware files `here <https://git.beagleboard.org/beagleboard/beaglebone-ai-64>`_ under the `hw` folder.

Production board boot media
****************************

- `BeagleBone AI-64 Rev B1`_

.. _software-updates:

Software Updates
******************

Follow instructions below to download the latest image for your BeagleBone AI-64:

1. Go to `BeagleBoard.org distro <https://www.beagleboard.org/distros>`_ page.
2. :ref:`filter-software-distribution-AI-64` from dropdown and download the image.

.. _filter-software-distribution-AI-64:

.. figure:: images/ch11/distros.*
   :align: center
   :alt: Filter Software Distributions for BeagleBone AI-64 

   Filter Software Distributions for BeagleBone AI-64

.. tip::
   You can follow the :ref:`flash-latest-image` guide for more information on 
   flashing the downloaded image to your board.

To see what SW revision is loaded into the eMMC check `/etc/dogtag`.
It should look something like as shown below,

.. code-block:: shell

   root@BeagleBone:~# cat /etc/dogtag
   BeagleBoard.org Debian Bullseye Xfce Image 2022-01-14

.. _rma-support:

RMA Support
*****************

If you feel your board is defective or has issues, request an Return Merchandise Application (RMA) by filling out the form at http://beagleboard.org/support/rma . You will need the serial number and revision of the board. The serial numbers and revisions keep moving. Different boards can have different locations depending on when they were made. The following figures show the three locations of the serial and revision number.

.. _trouble-shooting-video-output-issues:

Troubleshooting video output issues
*********************************************

.. warning:: 

   When connecting to an HDMI monitor, make sure your miniDP adapter is *active*. A *passive* adapter will not work. 
   See :ref:`accessories-cables_minidp_hdmi` accessories section for tested cables list.


.. _getting-help:

Getting Help
**************

If you need some up to date troubleshooting techniques, you can post your 
queries on link: `BeagleBoard.org forum <https://forum.beagleboard.org/tag/bbai64>`_

.. _bbai64-Change-history:

Change History
****************

This section describes the change history of this document and board. Document changes are not always a result of a board change. A board change will always result in a document change.

.. _bbai64-document-change-history:

Document Change History
=========================

This table seeks to keep track of major revision cycles in the documentation. Moving forward, we'll seek to align these version numbers across all of the various documentation.

.. _change-history-table, Change History:

.. list-table:: Table 1: Change History
   :header-rows: 1

   * - Rev
     - Changes
     - Date
     - By
   * - 0.0.1
     - AI-64 initial prototype
     - September 2021
     - James Anderson
   * - 0.0.2 
     - AI-64 final prototype 
     - December 2021  
     - James Anderson
   * - 0.0.3 
     - AI-64 initial production release 
     - June 9, 2022   
     - Deepak Khatri and Jason Kridner

.. _board-changes:

Board Changes
================

Be sure to check the board revision history in the schematic file in the `BeagleBone AI-64 git repository <https://git.beagleboard.org/beagleboard/beaglebone-ai-64>`_ . Also check the `issues list <https://git.beagleboard.org/beagleboard/beaglebone-ai-64/-/issues>`_ .

.. _rev-B:

Rev B
------

We are starting with revision B based on this being an update to the BeagleBone Black AI. However, because this board ended up being so different, we've decided to name it BeagleBone AI-64, rather than simply a new revision. This refers to the Seeed release on 21 Dec 2021 of "BeagleBone AI-64_SCH_Rev B_211221". This is the initial production release.

.. _BeagleBone-AI-64-Mechanical:

Mechanical Details
******************

.. _dimensions-and-weight:

Dimensions and Weight
======================

.. table:: Dimensions & weight

   +--------------------+----------------------------------------------------+
   | Parameter          | Value                                              |
   +====================+====================================================+
   | Size               | 104 * 83* 37 mm                                    |
   +--------------------+----------------------------------------------------+
   | Max heigh          | 23 mm                                              |
   +--------------------+----------------------------------------------------+
   | PCB Size           | 102.5*80*2.0 mm                                    |
   +--------------------+----------------------------------------------------+
   | PCB Layers         | 14 layers                                          |
   +--------------------+----------------------------------------------------+
   | PCB Thickness      | 2.0 mm                                             |
   +--------------------+----------------------------------------------------+
   | RoHS compliant     | Yes                                                |
   +--------------------+----------------------------------------------------+
   | Gross Weight       | 249g                                               |
   +--------------------+----------------------------------------------------+
   | Net Weight         | 193g                                               |
   +--------------------+----------------------------------------------------+

.. _silkscreen-and-component-locations:

Silkscreen and Component Locations
=====================================

.. figure:: images/hardware-design/board-dimensions.*
   :width: 400px
   :align: center 
   :alt: Board Dimensions
   
   Board Dimensions

.. figure:: images/hardware-design/top-silkscreen.*
   :width: 400px
   :align: center 
   :alt: Top silkscreen
   
   Top silkscreen

.. figure:: images/hardware-design/bottom-silkscreen.*
   :width: 400px
   :align: center 
   :alt: Bottom silkscreen
   
   Bottom silkscreen


.. _bbai64-pictures:

Pictures
*********

.. figure:: images/ch10/front.*
   :width: 400px
   :align: center 
   :alt: BeagleBone AI-64 front
   
   BeagleBone AI-64 front

.. figure:: images/ch10/back.*
   :width: 400px
   :align: center 
   :alt: BeagleBone AI-64 back
   
   BeagleBone AI-64 back

.. figure:: images/ch10/back-heatsink.*
   :width: 400px
   :align: center 
   :alt: BeagleBone AI-64 back with heatsink
   
   BeagleBone AI-64 back with heatsink

.. figure:: images/bbai64-45-front.*
   :width: 400px
   :align: center 
   :alt: BeagleBone AI-64 front at 45° angle
   
   BeagleBone AI-64 front at 45° angle

.. figure:: images/ch10/45-back.*
   :width: 400px
   :align: center 
   :alt: BeagleBone AI-64 back at 45° angle
   
   BeagleBone AI-64 back at 45° angle

.. figure:: images/ch10/45-back-heatsink.*
   :width: 400px
   :align: center 
   :alt: BeagleBone AI-64 back with heatsink at 45° angle
   
   BeagleBone AI-64 back with heatsink at 45° angle

.. figure:: images/ch10/feature.*
   :width: 400px
   :align: center 
   :alt: BeagleBone AI-64 ports
   
   BeagleBone AI-64 ports


