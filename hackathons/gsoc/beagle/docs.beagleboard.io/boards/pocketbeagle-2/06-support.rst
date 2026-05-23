.. _pocketbeagle-2-support:

Additional Support Information
##############################

All support for this design is through BeagleBoard.org community 
at `BeagleBoard.org forum <https://forum.beagleboard.org/tag/pocketbeagle-2>`_.

.. _pocketbeagle-2-certifications:

Certifications and export control
*********************************

Export designations
===================

* ECCN: 3A991.a
* HSCODE: 8517180050
* USHSCODE: 8543708800
* EUHSCODE: 8543709099
* UPC number: 841454123484

.. _pocketbeagle-2-hardware-design:

Hardware Design
****************

You can find all PocketBeagle 2 hardware files 
`here <https://openbeagle.org/pocketbeagle/pocketbeagle-2>`_ under the `design` folder.

Production board boot media
****************************

.. todo:: Add production image link with board revision information.

.. _pocketbeagle-2-software-updates:

Software Updates
******************

Follow instructions below to download the latest image for your PocketBeagle 2:

1. Go to `BeagleBoard.org distro <https://www.beagleboard.org/distros>`_ page.
2. On distros page, from dropdown select PB2 and download the image.

.. todo:: add distros page image selection for pocketbeagle-2

.. tip::

   You can follow the :ref:`flash-latest-image` guide for more information on 
   flashing the downloaded image to your board.

To see what SW revision is loaded into the eMMC check `/etc/dogtag`.
It should look something like as shown in example below,

.. code-block:: shell

   root@BeagleBone:~# cat /etc/dogtag
   BeagleBoard.org Debian Image 2024-02-24

.. _pocketbeagle-2-rma-support:

RMA Support
*****************

If you feel your board is defective or has issues, request an Return Merchandise Application (RMA) 
by filling out the form at http://beagleboard.org/support/rma . You will need the serial number and 
revision of the board. The serial numbers and revisions keep moving. Different boards can have different 
locations depending on when they were made. The following figures show the three locations of the serial 
and revision number.

.. _pocketbeagle-2-getting-help:

Getting Help
**************

If you need some up to date troubleshooting techniques, you can post your 
queries on link: `BeagleBoard.org forum <https://forum.beagleboard.org/tag/pocketbeagle-2>`_

.. _pocketbeagle-2-mechanical:

Mechanical Details
******************

.. _pocketbeagle-2-dimensions-and-weight:

Dimensions and Weight
======================

.. table:: Dimensions & weight

   +--------------------+----------------------------------------------------+
   | Parameter          | Value                                              |
   +====================+====================================================+
   | Size               | 56 x 35mm                                          |
   +--------------------+----------------------------------------------------+
   | Max heigh          | 13.6                                               |
   +--------------------+----------------------------------------------------+
   | PCB Size           | 55 x 35mm                                          |
   +--------------------+----------------------------------------------------+
   | PCB Layers         | 10--layers                                         |
   +--------------------+----------------------------------------------------+
   | PCB Thickness      | 1.6mm                                              |
   +--------------------+----------------------------------------------------+
   | RoHS compliant     | Yes                                                |
   +--------------------+----------------------------------------------------+
   | Net Weight         | 12.7g                                              |
   +--------------------+----------------------------------------------------+
   | Gross Weight       | 19g                                                |
   +--------------------+----------------------------------------------------+


