.. _beagleconnect-freedom-using-zephyr:

Using Zephyr
############

Developing directly in Zephyr will not be ultimately required for end-users 
who won't touch the firmware running on BeagleConnect™ Freedom and will instead
use the BeagleConnect™ Greybus functionality, but is important for early 
adopters as well as people looking to extend the functionality of the open 
source design. If you are one of those people, this is a good place to get 
started.

Equipment to begin development
******************************

There are many options, but using BeaglePlay gives a reasonable common
environment. Please adjust as you see fit.

Required
========

* `BeaglePlay with provided antennas <beagleplay-quick-start>`_
* `BeagleConnect Freedom with provided USB cable <beagleconnect-freedom-quick-start>`_
* `2x 5V/3A USB power adapters <accessories-power-supplies>`_
* `USB Type-C cable for use with BeaglePlay <accessories-cables>`_

Recommended
============

* Ethernet cable and Internet connection

Install the SDK on BeaglePlay
===============================

You can use BeaglePlay as the primary development board for setting up the Zephyr environment for BeagleConnect Freedom. 
To setup Zephyr on BeaglePlay, see :ref:`beagleplay-zephyr-development-setup`.

The instructions linked above setup the environment for targeting BeaglePlay's on CC1352. We need to change it to target 
BeagleConnect Freedom. You can directly go on to Step 5 under :ref:`zephyr_for_bcf`.

.. todo:: note the tested version of software for BeaglePlay

.. _zephyr_for_bcf:

Zephyr setup for BeagleConnect Freedom
========================================

To setup Zephyr on your machine for running modules on BeagleConnect Freedom, follow the given instructions :

1. First, install the Zephyr SDK bundle:
    
    .. code-block:: shell-session

        cd ~
        wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.15.1/zephyr-sdk-0.16.8_linux-aarch64_minimal.tar.gz
        wget -O - https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.16.8/sha256.sum | shasum --check --ignore-missing

.. tip::
    Find the all releases on `Zephyr SDK Tags <https://github.com/zephyrproject-rtos/sdk-ng/tags>`_ page, change to the version of the sdk according to your requirement.
    Also, you may replace ``aarach64``  with the host system you are currently working with.

1. Extract the Zephyr SDK bundle:
    
    .. code-block:: shell-session
        
        tar xf zephyr-sdk-0.16.8_linux-aarch64_minimal.tar.gz

.. important::
    
    It is recommended to extract the Zephyr SDK bundle at one of the following locations:

    .. code-block:: shell-session
            
        - $HOME
        - $HOME/.local
        - $HOME/.local/opt
        - $HOME/bin
        - /opt
        - /usr/local
        
    The Zephyr SDK bundle archive contains the ``zephyr-sdk-0.16.8`` directory and, when extracted under ``$HOME`` directory, 
    the resulting installation path will be ``<$HOME/zephyr-sdk-<version>``.

3. Run the Zephyr SDK bundle setup script:

    .. code-block:: shell-session
        
        cd zephyr-sdk-0.16.8
        ./setup.sh

4. Further, go on to setup the BeagleConnect Freedom (BCF)'s SDK.
    
    .. code-block:: shell-session
        
        west init -m https://github.com/zephyrproject-rtos/zephyr --mr sdk zephyr-beagle-cc1352-sdk
        cd $HOME/zephyr-beagle-cc1352-sdk
        python3 -m venv zephyr-beagle-cc1352-env

5. Export the required variables as given below:

    .. code-block:: shell-session

        echo "export ZEPHYR_TOOLCHAIN_VARIANT=zephyr" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo "export ZEPHYR_SDK_INSTALL_DIR=$HOME/zephyr-sdk-0.16.8" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo "export ZEPHYR_BASE=$HOME/zephyr-beagle-cc1352-sdk/zephyr" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo 'export PATH=$HOME/zephyr-beagle-cc1352-sdk/zephyr/scripts:$PATH' >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        echo "export BOARD=beagleplay" >> $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        source $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate
        west update
        west zephyr-export
        pip3 install -r zephyr/scripts/requirements-base.txt

.. note::
    
    You might need to change the version of the Zephyr-SDK based on the SDK setup done in Step 1.

Try demo applications
*********************

Now you can build various Zephyr applications

Build and flash Blinky
======================

.. note::
    Before building any example, ensure to run this command:
        
    .. code-block:: shell-session
            
        source $HOME/zephyr-beagle-cc1352-sdk/zephyr-beagle-cc1352-env/bin/activate

    
Run the build and flash commands. Make sure to connect the BeagleConnect Freedom to your computer before flashing.

    .. code-block:: shell-session

        cd $ZEPHYR_BASE
        west build zephyr/samples/basic/blinky
        west flash


Zephyr Documentation
=====================

You can refer to `Zephyr Getting Started <https://docs.zephyrproject.org/latest/develop/getting_started/index.html>`_ for further development!


Debug applications over the serial terminal
===========================================

.. todo::
    Add documentation to debug BCF zephyr application over serial terminal.
