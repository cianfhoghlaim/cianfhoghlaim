.. _beaglev-fire-softcore-usage:

How to use PicoRV Softcore on BeagleV-Fire
##########################################

Introduction
************

The PicoRV Softcore is a 32-bit RISC-V CPU subsystem on the BeagleV-Fire's FPGA fabric, functionally equivalent to the PRU subsystem on the BeagleBone Black. 
The core is designed for low-latency I/O operations and offloading smaller tasks like PWM, LEDS, etc .

Prerequisites
*************

To be able to use the softcore component, you'll need to have following packages installed on your host computer:

- gcc-riscv64-unknown-elf
- picolibc-riscv64-unknown-elf

.. note::

    These packages are used for compiling the code for the softcore.

For debian-based systems like ubuntu, you can use following commands:

.. code-block:: console

    sudo apt install gcc-riscv64-unknown-elf picolibc-riscv64-unknown-elf

If you are using any other linux distro these packages can be downloaded from respective package managers.
But, it is highly recommended to use docker for accurate results.

`Docker installation steps <https://docs.docker.com/engine/install>`_.

Once you have docker installed:

1. Start a container with ubuntu image.
2. Install the required toolchain using above mentioned command (remember not to use 'sudo' in docker).

.. code-block:: console

    Sudo docker run -it ubuntu:latest

After installing the necessary tools, you are all set for using the Softcore. 

How to use the Softcore
***********************

1. Boot the softcore with firmware
==================================

Step 1
------

Navigate to ``sources/FPGA-design/script_support/components/SOFTCORE/PICO_RISCV/firmware`` in the BeagleV-Fire repository.

Step 2
------

Edit the firmware.c file by adding your code in the main function. You can create your own custom file but remember to use firmware.h file for pre-defined functions to access gpios.

Step 3
------

Now run the ``generatehex.sh`` to compile the code. (remember to edit the file name in the script of you are using custom file)

.. code-block:: console

    . ./generatehex.sh

If you are using docker clone the repository on your docker container or use docker copy, then compile the program and use docker copy to obtain the hex file.

To copy file from local system to docker container:

.. code-block:: console

    docker cp ./path/to/file CONTAINER:/path/to/directory

To copy file from docker container to local system:

.. code-block:: console

    docker cp CONTAINER:/path/to/file /path/to/directory

To check the name of docker 'CONTAINER':

.. code-block:: console 

    docker ps -a

This will list all the running and stopped containers
To restart a stopped container, use:

.. code-block:: console

    sudo docker start name_of_container -i 

Step 4
------

Select PicoRV build option for bitstream generation

Once the code is compiled, build the bitstream using the 'build-bitstream.py' script.

.. code-block:: console

    python build-bitstream.py ./build-options/picorv-softcore.yaml 

.. note::

    The Gitlab CI does not support the softcore code compilation yet, so the bitstream must be generated locally.

Step 5
------

Program BeagleV-Fire With Your `Custom Bitstream <https://docs.beagleboard.org/boards/beaglev/fire/demos-and-tutorials/gateware/customize-cape-gateware-verilog.html>`_.


2. Programming the softcore in run-time
=======================================

Step 1
------

- Program the softcore with custom bitstream with picorv-softcore build-option.
- Follow the steps mentioned in previous section.

Step 2
------

- Edit and compile your new code in your local machine.(BeagleV-Fire does not support on-board compilation for softcore programs yet, this feature will be added soon.)
- Follow Steps 2 and 3 in previous section for compiling your new program.

Step 3
------

Copy the firmware directory from BeagleV-Fire repository to your board.

.. code-block:: console

    sudo scp -r path/to/firmware beagle@192.168.7.2:/home/beagle 

Step 4
------

- Overwritting softcore's program memory.
- Compile the 'AXI_test.c' file using gcc and execute it.

.. code-block:: console

    gcc -o AXI_test AXI_test.c
    sudo ./AXI_teste 


- This will open a interactive menu with various option that you can try out and access the program memory of the softcore.
- Here we will select *option 2* to upload the hex file we just compiled to the softcore.

.. note::

    This compilation in step 2 is to generate a hex file to program the Softcore, while the compilation in Step 3 is performed to command the Linux system on-board to access the program memory of the Softcore.

.. note::
    
    The filename in **AXI_test.c** for the hex file is set as ``firmware.hex``, so make sure the name of the hex file you compiled is the same else change the filename pointer in **AXI_test.c**.

Repository
==========

`PicoRV softcore builder <https://openbeagle.org/gsoc/2024/riscv-io-core/>`_.
