.. _beaglev-fire-mchp-fpga-tools-installation-guide:

Microchip FPGA Tools Installation Guide
#########################################

Instructions for installing the Microchip FPGA tools on a Ubuntu 20.04 or Ubuntu 22.04 desktop.

.. important::

   We will be providing instances of Libero that you can run from git.beagleboard.org's gitlab-runners such that you do not need to install the tools on
   your local machine.

.. todo::

   Make sure people know about the alternative and we provide links to details on that before we send them down this process.


Install Libero 
**************

.. note:: Libero 2023.2, 2024.1 or 2024.2 should work. 2024.2 is used as an example.

Create a folder named Microchip in your /home folder

- Download installer from the `Microchip's fpga and soc design tools section <https://www.microchip.com/en-us/products/fpgas-and-plds/fpga-and-soc-design-tools/fpga/libero-software-later-versions>`_.
- Install Libero

.. code-block::

  unzip Libero_SoC_v2024.2_lin.zip

  ./launch_installer.sh

.. important:: 
    Do not use the default location suggested by the Libero installer. 
    Instead of /usr/local/Microchip/Libero_SoC_v2024.2 install into ~/Microchip/Libero_SoC_v2024.2
    
Run the post installation script which will install missing packages:

.. code-block::

  sudo /home/$USER/Microchip/Libero_SoC_v2024.2/Logs/req_to_install.sh

No need to run the FlashPro hardware installation scripts. This will be taken care of as part of the SoftConsole installation.

Install SoftConsole 2022.2
***************************

- Download installer from `Microchip website <https://www.microchip.com/en-us/products/fpgas-and-plds/fpga-and-soc-design-tools/soc-fpga/softconsole>`_.

.. code-block::

  sudo chmod +x Microchip-SoftConsole-v2022.2-RISC-V-747-linux-x64-installer.run

  ./Microchip-SoftConsole-v2022.2-RISC-V-747-linux-x64-installer.run

Accept the license, Click Forward, Finish.

Perform the post installation steps as described in the html file opened when you click Finish.

.. important:: 

  Please pay special attention to the "Enabling non-root user to access FlashPro" section of the post-installation instructions. 
  This will actually allow you to program the board using Libero.

Install the Libero licensing daemon
************************************

Download the latest 64 bit Licensing Daemons from the `Microchip's fpga and soc design tools section <https://www.microchip.com/en-us/products/fpgas-and-plds/fpga-and-soc-design-tools/fpga/libero-software-later-versions>`_

* `Linux_Licensing_Daemon_11.19.6.0_64-bit.tar.gz <https://ww1.microchip.com/downloads/secure/aemdocuments/documents/fpga/media-content/FPGA/daemons/Linux_Licensing_Daemon_11.19.6.0_64-bit.tar.gz>`_
* `Windows_Licensing_Daemon_11.19.6.0_64-bit.zip <https://ww1.microchip.com/downloads/secure/aemdocuments/documents/fpga/media-content/FPGA/daemons/Windows_Licensing_Daemon_11.19.6.0_64-bit.zip>`_


Older Daemon downloads can be found at `Microchip's daemons section <https://www.microchip.com/en-us/products/fpgas-and-plds/fpga-and-soc-design-tools/fpga/licensing>`_


* `Linux_Licensing_Daemon_11.16.1_64-bit.tar.gz <https://ww1.microchip.com/downloads/aemdocuments/documents/fpga/media-content/FPGA/daemons/Linux_Licensing_Daemon_11.16.1_64-bit.tar.gz>`_
* `Windows_Licensing_Daemon_11.16.1_64-bit.zip <https://ww1.microchip.com/downloads/aemdocuments/documents/fpga/media-content/FPGA/daemons/Windows_Licensing_Daemon_11.16.1_64-bit.zip>`_


Copy the downloaded file to the Microchip directory within your home directory and untar it.

.. code-block::

  cd ~/Microchip

  tar -xvf Linux_Licensing_Daemon_11.19.6.0_64-bit.tar.gz


Install the Linux Standard Base:

.. code-block:: 

  sudo apt-get update

  sudo apt-get -y install lsb


Request a Libero Silver license
********************************

- Visit `microchip's fpga software products page <https://www.microchipdirect.com/fpga-software-products>`_
- Choose "Libero Silver 1Yr Floating License for Windows/Linux Server" from the list.
- Enter your MAC address and click register. 
  
.. note::
    
    A MAC address looks something like 12:34:56::78:ab:cd when you use the "ip address" command to find out 
    its value on your Linux machine. However, you need to enter it as 123456abcd in this dialog box.

You will get an email with a License.dat file. Copy it into the ~/Microchip/license directory. Replace `<put.hostname.here>` in `License.dat` with `localhost` and add Linux_Licensing_Daemon as the path to the daemons.

The top of your license file should look something like this after editing. Your daemon files should be located in the  Linux_Licensing_Daemon folder inside the Microchip folder.

.. code-block:: text

   SERVER localhost 001584731680 1702
   DAEMON actlmgrd  Linux_Licensing_Daemon/actlmgrd
   # Starting Libero SOC v2024.2, customers are recommended ...
   # DAEMON mgcld Linux_Licensing_Daemon/mgcld
   DAEMON saltd Linux_Licensing_Daemon/saltd
   VENDOR snpslmd  Linux_Licensing_Daemon/snpslmd


Execute tool setup script
***************************

Download the script:

.. literalinclude:: ./setup-microchip-tools.sh
    :caption: Libero environment and license setup script
    :language: bash

:download:`setup-microchip-tools.sh <./setup-microchip-tools.sh>`

Details:

You can create a folder named FPGA-Tools-Setup and store the file there, although this is not required, as long as it is inside the Microchip folder.

You shouldn't need to edit the script, as long as you have installed Libero inside a folder that follows the Libero_SoC_vXXXX.X format, or if you have multiple Libero versions installed and want to select a preferred one to use.

Source the script:

.. code-block::

  sudo chmod +x setup-microchip-tools.sh

  . ./setup-microchip-tools.sh

.. important:: 
  
  Do not forget the leading dot. It matters. You will need to run this every time you restart your machine. 

Optionally, add this to the end of your `~/.bashrc` file to avoid running it each time on startup.

First, open `~/.bashrc`:

.. code-block:: bash

   nano ~/.bashrc

Then, add the following lines at the end:

.. code-block:: bash

   cd /home/$USER/Microchip/
   . ./setup-microchip-tools.sh

You can then start Libero to open an existing Libero project.

.. code-block:: 

  libero

However you will more than likely want to use Libero to run a TCL script that will build a design for you.

.. code-block:: 
    
  libero SCRIPT:BUILD_A_DESIGN.tcl