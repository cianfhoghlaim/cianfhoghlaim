.. _beagleconnect-overview:

Overview
#########

Greybus
*******

I will be taking information from the `Greybus LWN article <https://lwn.net/Articles/715955/>`_. So feel free to check it out.

Greybus was initially designed for Google's Project Ara smartphone (which is discontinued now), but the first (and only) product released with it is Motorola's Moto Mods. It was initially merged for potential use by kernel components that need to communicate in a platform-independent way.

The `Greybus specification <https://github.com/projectara/greybus-spec>`_ provides device discovery and description at runtime, network routing and housekeeping, and class and bridged PHY protocols, which devices use to talk to each other and to the processors. The following figure shows how various parts of the kernel interact with the Greybus subsystem.

.. image:: images/greybus.webp
   :align: center
   :alt: Greybus subsystem


There are three main entities in the Greybus network:

#. **AP:** It refers to the host CPUs, i.e., CPUs running Linux in most cases. It is responsible for administrating the Greybus network via the SVC.
#. **SVC:** The SVC represents an entity within the Greybus network that configures and controls the Greybus (UniPro) network, mostly based on the instructions from the AP. All module insertion and removal events are first reported to the SVC, which in turn informs the AP about them using the SVC protocol.
#. **Module:** A module is the physical hardware entity that can be connected or disconnected statically (before powering the system on) or dynamically (while the system is running) from the Greybus network. Once the modules are connected to the Greybus network, the AP and the SVC enumerate the modules and fetch per-interface manifests to learn about their capabilities.

While Greybus is a great protocol, the implementation is tightly coupled with the UniPro transport. This makes it challenging to use Greybus in other modes of transport.


BeagleConnect™ Technology Mission
**********************************

BeagleConnect™ Technology aims to use Greybus outside of the traditional Greybus network. This includes using transports other than UniPro (such as 6lowpan), using embedded devices running `Zephyr RTOS <https://zephyrproject.org/>`_ as modules, emulating :term:`SVC <BeagleConnect SVC>` in co-processor, etc. This makes BeagleConnect™ much more flexible than what traditional greybus seems to support. Here is a diagram of the general BeagleConnect™ setup:

.. image:: images/software_prop_transport.svg
   :align: center
   :alt: BeagleConnect Technology arbitrary transport

The :term:`SVC <BeagleConnect SVC>` is either emulated in userspace software in the SOC (gbridge) or in a co-processor (e.g., in :ref:`BeaglePlay <beagleplay-home>`). The arbitrary transport can be anything from 6lowpan (for long range) to ethernet or optical cables (for max speed). Finally, greybus nodes such as BeagleConnect™ Freedom running Greybus Zephyr firmware allow the use of `mikroBUS <https://www.mikroe.com/mikrobus>`_ which opens a host of Plug and Play possibilities for peripherals.


Why should you use BeagleConnect™?
***********************************

.. image:: images/SoftwareProp.jpg
   :align: center
   :alt: BeagleConnect Technology arbitrary transport

#. **Open-source:** The `Greybus Spec <https://github.com/projectara/greybus-spec>`_ is open-source and a part of the Linux kernel. This makes it easy to use and personalize for your use case. Being part of the Linux Kernel also provides it a level of reliability that most similar solutions lack.

#. **Network agnostic:** BeagleConnect™ allows Greybus to be network agnostic. This means it can be used over networks like 6lowpan, which has incredible wireless range, or over optical networks for high-throughput, low-latency use cases.

#. **Rapid Prototyping:** Any device (e.g., `mikroBUS add-on boards <https://www.mikroe.com/click-boards>`_) connected to the greybus node can be accessed from the Linux host. In this setup, only the Linux host needs to have device drivers. We remove the need to write drivers for the OS our node (the device with which peripheral is actually connected) runs on (e.g. `Zephyr RTOS Project <https://www.zephyrproject.org>`_, `Nuttx <https://nuttx.apache.org>`_, etc). This allows being able to prototype devices by just creating a Linux driver instead of having to write drivers for each individual embedded OS.

#. **Star topology IoT and IIoT networks:** Greybus was designed to be low level and allow hot-plugging of remote devices. This means a greybus network does not need to use bulky protocols like REST and data formats like JSON. This in turn allows using relatively low-powered device as nodes.

#. **Use of Existing Infrastructure:** Since BeagleConnect™ devices show up as normal Linux devices, they work with existing local device management software. This eliminates need for propritory and custom solutions to monitor devices. Instead Linux host can directly read peripherals on nodes using standard Linux tools such as `iio_readdev <https://wiki.analog.com/resources/tools-software/linux-software/libiio/iio_readdev>`_.

#. **Infinite Customization:** With support for `mikroBUS add-on boards <https://www.mikroe.com/click-boards>`_, capabilities of BeagleConnect™ nodes can be expanded dramaticically with little to no fiddling.

.. note::

    The above is just a glimpse of what BeagleConnect™ can do. Many more use cases can be explored. If you have any ideas, feel free to reach out to us.


What's next?
************

BeagleConnect™ is still in its early stages. We are working on making it more robust and easy to use. We are trying to provide a complete experience for testing BeagleConnect™ Technology in our BeaglePlay and BeagleConnect™ boards.

We are looking for more people to join us in improving BeagleConnect™ technology. Feel free to reach out to us at `Discord <https://discordapp.com/channels/1108795636956024986/1189277127590289469>`_ or `BeagleBoard Forum <https://forum.beagleboard.org/>`_.

Contributions
*************
- `Greybus LWN article <https://lwn.net/Articles/715955/>`_
