.. _intro-zephyr:

Introduction to Zephyr RTOS
###########################

The Zephyr OS is built on a lightweight kernel optimized for resource-constrained 
and embedded systems, making it an excellent fit for BeagleBoard projects. From simple 
environmental sensors and LED-based designs to advanced embedded controllers, smart 
devices, and IoT wireless applications. Zephyr is a scalable RTOS that can be used in
multiple architectures and platforms.

This article will focus on giving a starting point to learning Zephyr using a Beagleboard.

Why Zephyr?
***********

- **Scalable**: Zephyr is designed to be scalable, from simple embedded systems to complex IoT applications.
- **Modular**: Zephyr is designed to be modular, allowing you to use only the components you need.
- **Open Source**: Zephyr is open-source, allowing you to modify and contribute to the project.
- **Cross-platform**: Zephyr supports multiple architectures and platforms.
- **Community**: Zephyr has a large community of developers and contributors.

Getting Started with Zephyr
****************************

To get started with Zephyr, you will need to follow `Getting Started Guide by Zephyr 
<https://docs.zephyrproject.org/latest/getting_started/index.html>`_. 
By following the guide, you will be able to set up your development environment and get to 
try out a zephyr sample applications.

Delving into Zephyr
*******************

Once you have set up your development environment and tried out the sample applications,
Let's delve into Zephyr by creating a simple application. We will now delve into breaking 
the `blinky sample application <https://docs.zephyrproject.org/latest/samples/basic/blinky/README.html#blinky>`_ 
and understand how it works.

Here are the files in a simple Zephyr application:

Let's pull blinky sample application from Zephyr repository to zephyrproject directory.

.. code-block:: shell-session

    cp -r zephyrproject/zephyr/samples/basic/blinky zephyrproject/app

.. code-block:: none

   app
    ├── app.overlay
    ├── CMakeLists.txt
    ├── prj.conf
    ├─ src
    |   └── main.c
    └── app.overlay


- **CMakeLists.txt**: This file is used by CMake to build the application.
- **app.overlay**: This file is used to configure the application changes based on the base device-tree.
- **prj.conf**: This file is used to configure the Kconfig fragment that specifies application-specific values.
- **VERSION**: This file is used to specify the version of the application.
- **src/main.c**: This file contains the main application code.

Let's take a look at the contents of the `main.c` file:

.. code-block:: c

    #include <stdio.h>
    #include <zephyr/kernel.h>
    #include <zephyr/drivers/gpio.h>

These include statements include the necessary header files for the application such 
as `stdio.h` for printf functions , `kernel.h` for kernel APIs like ms_sleep(), and 
`gpio.h` for GPIO APIs for GPIO related functions.

.. code-block:: c

    #define LED_NODE DT_ALIAS(led0)

As Zephyr uses a device tree to configure the hardware, this macro is used to get the 
device tree node for the LED by resolving the alias `led0` alias present in the device tree,
enabling the application to use the LED.

.. code-block:: c

    static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);

``GPIO_DT_SPEC_GET`` fetches the GPIO configuration for led0.

.. note::

    build error on this line means your board is unsupported.

.. code-block:: c

    if (!gpio_is_ready_dt(&led)) {
    return 0;
    }

This code checks if the GPIO is ready to use, if not it returns 0.

.. code-block:: c

    ret = gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);

This code configures the GPIO pin as an output pin and sets the initial state to active.

.. note::

    There are many other options other than GPIO_OUTPUT_ACTIVE, like GPIO_OUTPUT_INACTIVE, GPIO_INPUT, etc.
    For more visit `Zephyr GPIO API <https://docs.zephyrproject.org/apidoc/latest/group__gpio__interface.html>`_,
    GPIO input/output configuration flag section.

.. code-block:: c

    ret = gpio_pin_toggle_dt(&led);

The ``gpio_pin_toggle_dt`` API helps in toggling the LED’s state

.. code-block:: c

    k_msleep(1000);

This code makes the application sleep for 1000 milliseconds. part of the kernel API.

As you have seen in this sample, there was not a single bit of hardware-specific code. 
This is the beauty of Zephyr, which abstracts the hardware and provides a unified API

Building the Application
========================

To build the application, you need to run the following commands:

.. code-block:: none

    west build -b <board-name>. 

.. note::

    West is a tool that helps in managing multiple repositories and build systems.
    For more information, visit `West documentation <https://docs.zephyrproject.org/latest/guides/west/index.html>`_.

After building the application, you will get the `zephyr.hex` file in the `build/zephyr` directory.

Flashing the Application
========================

To flash the application, you need to run the following command:

.. code-block:: none

    west flash

.. note::

    1. To use west flash in BeagleConnect Freedom or BeaglePlay, it requires ``cc1352-flasher`` tool to be installed.

    .. code-block:: none

        pip3 install cc1352-flasher
            
    2. At the moment, BeagleBone AI-64 doesn't support west flash. Please use the 
        `AI-64 documentation <https://docs.zephyrproject.org/latest/boards/beagle/beaglebone_ai64/doc/index.html>`_ 
        provided by Zephyr for flashing the application.
    3. At the moment, BeagleV-Fire doesn't support west flash. Please use the 
        `BeagleV-Fire documentation <https://docs.zephyrproject.org/latest/boards/beagle/beaglev_fire/doc/index.html>`_ 
        provided by Zephyr for flashing the application.

Result
======

After flashing the application, you will see the LED blinking every second.

Recommended Reading
*******************

- `Zephyr Documentation <https://docs.zephyrproject.org/latest/index.html>`_
- `Zephyr RTOS tutorial <https://github.com/maksimdrachov/zephyr-rtos-tutorial>`_
- `awesome zephyr RTOS <https://github.com/zephyrproject-rtos/awesome-zephyr-rtos>`_
