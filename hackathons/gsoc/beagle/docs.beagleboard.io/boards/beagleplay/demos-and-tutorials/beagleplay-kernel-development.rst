.. _beagleplay-kernel-development:

BeaglePlay Kernel Development
#############################

This guide is for all those who want to kick start their kernel development
journey on the TI AM625x SoC Based BeaglePlay.

Getting the Kernel Source Code
******************************

The Linux kernel is hosted on a number of servers around the world. The main
repository is hosted on the kernel.org website, but there are also mirrors
hosted by other organizations, such as GitHub and Bootlin.

The `Linux Torvalds tree <https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/>`_
is the most up-to-date source of the Linux kernel.
It is used by Linux distributions and other projects to build their own kernels.
The tree is also a popular destination for kernel developers who want to
contribute to the kernel.

Kernel sources can directly be fetched using ``git``:

.. code-block:: bash

        git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git

A big advantage of using ``git`` to fetch the kernel sources is that you'll easily be able to manage your
changes, keeping track of what you might edit. If you are looking for a quicker way to download a single
version of the Linux kernel sources to get started, you might consider fetching a "tarball" using ``wget``.

.. code-block:: bash

       wget https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/snapshot/linux-6.6.tar.gz
       tar xf linux-6.6.tar.gz

.. note::

       While fetching a tarball with ``wget`` might be faster than fetching the full history with ``git``,
       the ability to track changes with ``git`` is significant.

For more information on using ``git``, see :ref:`beagleboard-git-usage`.

Preparing to Build
******************

These instructions should be valid on any Debian-based system, but were tested on a BeaglePlay itself.

.. code-block:: bash

        sudo apt update
        sudo apt install -y fakeroot build-essential libncurses-dev xz-utils libssl-dev flex libelf-dev bison debhelper

Configuring the Kernel
**********************

The easiest way to configure the kernel is to start with a configuration known to work. A running BeaglePlay
is a great source for that configuration, as it gets compiled into the running kernel.

.. note::

        If you don't have a BeaglePlay booted, you can copy a known good kernel configuration from the
        BeagleBoard.org Linux git repository at https://git.beagleboard.org/beagleboard/linux. On each release
        branch, the last commit typically contains a ``bb.org_defconfig`` file. For BeaglePlay, you should
        look for an ``arm64`` branch.

        Example: https://git.beagleboard.org/beagleboard/linux/-/blob/f47f74d11b19d8ae2f146de92c258f40e0930d86/arch/arm64/configs/bb.org_defconfig

Running on a BeaglePlay, you can configure your kernel using ``/proc/config.gz``. You'll also want
to ``make olddefconfig`` to update your config for the newer kernel. If you want to look at configuration
options that haven't previously been configured, then use ``make oldconfig`` instead. Once you've
got an initial configuration, you can edit the configuration various ways including ``make menuconfig``.

.. code-block:: bash

        cd linux-6.6
        zcat /proc/config.gz > .config
        make olddefconfig

You can also take advantage of the running system to provide the WiFi regulatory database (regulatory.db). This
is needed such that your kernel sets the WiFi signals appropriately for compliance with regional restrictions.

For more information, see `Linux wireless regulatory documentation <https://www.kernel.org/doc/html/latest/networking/regulatory.html>`_ and
the signed database images at https://git.kernel.org/pub/scm/linux/kernel/git/sforshee/wireless-regdb.git/tree/.

.. code-block:: bash

        mkdir -p firmware
        cp /lib/firmware/regulatory.db* firmware/

Building the Kernel
*******************

Once you're set on your configuration, you'll want to build the kernel and build any external modules. To
make things simpler to install, we'll create a Debian package of the kernel.

.. note::

        Building the kernel on BeaglePlay might take a while. For me, it took about an hour.

.. code-block:: bash

        cd ..
        make -C ./linux-6.6 -j4 KDEB_PKGVERSION=1xross bindeb-pkg

Installing and Booting the Kernel
*********************************

.. important::

        In case your new kernel fails, you'll want to be prepared to either reflash the board
        or to use a serial cable to halt u-boot and request loading a working kernel still
        available on the board.

        See :ref:`beagleplay-serial-console` to setup access over the debug serial port.

.. _play-dpkg-install-kernel:

.. code-block:: bash
    :caption: Install 6.6.0 kernel and reboot

        sudo dpkg -i linux-image-6.6.0_1xross_arm64.deb
        sudo shutdown -r now

As long as the kernel you built has no significant issues, you'll boot back into a
running system.

If there was a boot or connectivity failure, you can try an alternate connectivity method, such as
the :ref:`beagleplay-serial-console` or Ethernet, or you can reflash the board and try again from
a known good kernel source.

For me, the linux-6.6 kernel booted fine, but the beagleplay.local (mDNS/Avahi broadcast) address
did not show up right away. I was able to find the BeaglePlay hosted WiFi access point, the
connection to my local WiFi network, connect over Ethernet and connect over USB network. The `/dev/play` directory
did not exist, but the `/dev/bone` directory did, so this gives me a good starting point for
generating some patches to update the mainline kernel. :-D

See :ref:`beagleboard-linux-upstream` for more next steps by providing updates you make to the kernel
to the upstream repository for everyone to benefit and for you to benefit from on future kernel
versions.

Kernel Debug
************

Consider reading the kernel documentation
on `debugging via gdb <https://www.kernel.org/doc/html/latest/dev-tools/gdb-kernel-debugging.html>`_.

Also, consider the the TI Linux Board Porting Series, specifically the module
on `debugging with JTAG in CCS <https://www.ti.com/video/3874392631001?keyMatch=LINUX%20KERNEL%20DEBUG>`_.

References
**********

- For more details on the Linux kernel build system, see `The kernel build system <https://www.kernel.org/doc/html/latest/kbuild/index.html>`_ on kernel.org.

- For additional guidance, see the `official TI-SDK documentation for AM62X <https://software-dl.ti.com/processor-sdk-linux/esd/AM62X/latest/exports/docs/linux/Foundational_Components_Kernel_Users_Guide.html>`_
