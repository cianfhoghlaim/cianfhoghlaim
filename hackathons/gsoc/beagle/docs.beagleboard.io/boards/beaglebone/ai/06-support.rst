.. _bbai-support:

Additional Support Information
##############################

All support for BeagleBone AI design is through BeagleBoard.org 
community at `BeagleBoard.org forum <https://forum.beagleboard.org/tag/bbai>`_.

.. todo::

  Reference https://docs.beagleboard.org/latest/intro/support/index.html and
  https://beagleboard.org/resources

  Related TI documentation: http://www.ti.com/tool/BEAGLE-3P-BBONE-AI

Production board boot media
****************************

.. todo:: Add production boot media link in ``_static/epilog/production.image`` and reference it here.

.. _beaglebone-ai-regulatory:

REGULATORY, COMPLIANCE, AND EXPORT INFORMATION
*************************************************

-  Country of origin: PRC
-  FCC: 2ATUT-BBONE-AI
-  CE: TBD
-  CNHTS: 8543909000
-  USHTS: 8473301180
-  MXHTS: 84733001
-  TARIC: 8473302000
-  ECCN: 5A992.C
-  CCATS:
   `Z1613110/G180570 <https://git.beagleboard.org/beagleboard/beaglebone-ai/-/tree/master/regulatory/Validation_Z1613110.pdf>`__
-  RoHS/REACH: TBD
-  Volatility: TBD

.. _beaglebone-ai-mechanical:

Mechanical Information
************************

-  Board Dimensions: 8.9cm x 5.4cm x 1.5cm
-  Board Net Weight 48g
-  Packaging Dimensions: 13.8cm x 10cm x 4cm
-  Gross Weight (including packaging): 110g
-  3D STEP model:
   https://git.beagleboard.org/beagleboard/beaglebone-ai/-/tree/master/Mechanical


.. _beaglebone-ai-change-history:

Change History
***************

Rev A0
=======

Initial prototype revision. Not taken to production.
eMMC flash image provided by Embest.

Rev A1
=======

Second round prototype.

-  Fixed size of mounting holes.
-  Added LED for WiFi status.
-  Added microHDMI.
-  Changed eMMC voltage from 3.3V to 1.8V to support HS200.
-  Changed eMMC from 4GB to 16GB.
-  Changed serial debug header from 6-pin 100mil pitch to 3-pin 1.5mm pitch.
-  Switched expansion header from UART4 to UART5. The UART4 pins were used for the microHDMI.

eMMC flash image provided by Embest.

Rev A1a
========

Alpha pilot-run units and initial production.

-  `Added pull-down resistor on serial debug header RX
   line <https://git.beagleboard.org/beagleboard/beaglebone-ai/-/issues/24>`__.

Alpha pilot-run eMMC flash image:
https://debian.beagleboard.org/images/bbai-pilot-20190408.img.xz

Production eMMC flash image:
http://debian.beagleboard.org/images/am57xx-eMMC-flasher-debian-9.9-lxqt-armhf-2019-08-03-4gb.img.xz

Rev A2
=======

Proposed changes.

-  `HW: need pull-down on console uart RX line 
   <https://git.beagleboard.org/beagleboard/beaglebone-ai/-/issues/24>`__.

-  `HW: position of microSD may impact existing case designs 
   <https://git.beagleboard.org/beagleboard/beaglebone-ai/-/issues/25>`__.

-  `HW: P9.13 does not have a GPIO 
   <https://git.beagleboard.org/beagleboard/beaglebone-ai/-/issues/22>`__.

-  `HW: HDMI hotplug detection not working 
   <https://git.beagleboard.org/beagleboard/beaglebone-ai/issues/19>`__.

-  `HW: add extra DCAN 
   <https://git.beagleboard.org/beagleboard/beaglebone-ai/issues/20>`__.

-  `HW: wire mods required to enable JTAG 
   <https://git.beagleboard.org/beagleboard/beaglebone-ai/issues/21>`__.

-  `HW: Small I2C nvmem/eeprom for board identifier 
   <https://git.beagleboard.org/beagleboard/beaglebone-ai/issues/23>`__.

.. _beaglebone-ai-pictures:

Pictures
*********

.. image:: images/BB_AI_Front.jpg
    :align: center

.. image:: images/BB_AI_Back.jpg
    :align: center
