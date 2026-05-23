.. _beagleV-fire-gateware-builder:

How to build the BeagleV-Fire Gateware on Windows
#############################################################################

Introduction
============
The BeagleV Fire gateware builder is a Python script that builds both the PolarFire SoC HSS bootloader and Libero FPGA project into a single programming bitstream. 
It uses a list of repositories/branches specifying the configuration of the BeagleV Fire to build.

Prerequisites
=============

Tools
-----------
To be able to use the bitstream builder on Windows, you will need to install the following tools:

- Msys2-Mingw
- Make 
- wsl

Please follow the installation instructions for Msys2 available at https://www.msys2.org/wiki/MSYS2-installation/

When installing *make* in your mysys2 terminal you're recommended to use the default command 

.. code-block:: 

    pacman -S make

For those requiring a specific version of *make*, refer to the porting guide at https://www.msys2.org/wiki/Porting/

.. code-block::

    pacman -S <target>-make

Ensure that the *Msys2* bin path (e.g., *C:\msys64\usr\bin*) is added to your system's environment variable PATH.

To enable and install WSL, follow these steps:

- Search for "Turn Windows features on or off" in the Windows start menu.
- Select "Windows Subsystem for Linux" and click OK.
- Open a command prompt as an administrator and execute:


.. code-block::

    wsl.exe --install


After installing the necessary tools, proceed to the repository and follow the instructions in the README to build the bitstream on Windows


Repository
------------
Access the BeagleV-Fire gateware builder repository at https://openbeagle.org/cyril-jean/gateware-maintenance/ 


.. note::

    If you encounter an end-of-line error (CRLF/LF) during the build process, change the local Git configuration *core.autocrlf* to false and clone the repository again


    .. code-block::

        git config --global core.autocrlf false



.. note::  

    - Should the build fail due to an unrecognized Python package, despite the package being installed, it may be due to multiple Python/pip versions. Reinstall the package using.

    .. code-block::
        
        python -m pip install <package-name>

    - Verify that the LM_LICENSE_FILE environment variable includes licenses for all required programs to avoid silent errors during the build process




