.. _beagleboard-linux-upstream:

Upstream Kernel Contributions
#############################

.. note::
    For detailed information on Kernel Developmement checkout the official
    `kernel.org <https://www.kernel.org/doc/html/latest/>`_
    kernel docs.

For a person or company who wishes to submit a change to the Linux kernel,
the process can sometimes be daunting if you’re not familiar with “the system.”
This text is a collection of suggestions which can help you get started and greatly increase the chances
of your change being accepted.

.. note:: This version is an unofficial draft and is subject to change.

Pre-requisites
***************

The following are the skills that are needed before you actually start to contribute to the linux kernel:

    - :ref:`linux-upstream-more-git`
    - :ref:`linux-upstream-c-programming`
    - :ref:`linux-upstream-cross-arch`
    - :ref:`linux-upstream-embedded-buses`
    - :ref:`linux-upstream-drivers`
    - :ref:`linux-upstream-device-trees`

For more guidance, check out the :ref:`linux-upstream-additional-resources`.

.. _linux-upstream-more-git:

More Git!
*********

It is highly recommended that you go through :ref:`beagleboard-git-usage` before starting
to read and follow these guidelines. You will need to have a proper git setup on your
computer in order to effectively follow these steps.

Creating your first patch
=========================

When you first enter the world of Linux Kernel development from a background in
contributing over gitlab or github, the terminologies slightly change.

Your Pull Requests (PRs) now become Patches or Patch Series. You no longer just
go to some website and click on a "Create Pull Request" button. Whatever code/changes you
want to add will have to be sent as patches via emails.

As an example, let's consider a commit to add the git section to these docs.
I stage these changes first using ``git add -p``.

.. code-block::

    diff --git a/contribution/contribute.rst b/contribution/contribute.rst
    index def100b..0af08c5 100644
    --- a/contribution/contribute.rst
    +++ b/contribution/contribute.rst

Then, commit the above changes.

**Note:** Don't forget to make your commit message descriptive of the feature
you are adding or the work that you have done in that commit. The commit
has to be self explanatory in itself. Link any references if you have used
and paste any logs to prove your code works or if there is a fix.

.. code-block::

    git commit -vs

    [linux-contrib 3bc0821] contribute.rst: Add git section
     1 file changed, 27 insertions(+), 1 deletion(-)

Now, let's say we want to send this new feature to upstream kernel. You then have to create
a patch file using the following command:

.. code-block::

    git format-patch -1 HEAD

    0001-contribute.rst-Add-git-section.patch

This will generate one file that is generally referred to as the patch file.
This is what you will now be sending upstream in order to get your patch merged.
But wait, there are a few more things we need to setup for sending a patch via e-mail.
That is, of course your email!

For configuring your email ID for sending patches refer to this excellent stackoverflow thread,
`configure git-send-email
<https://stackoverflow.com/questions/68238912/how-to-configure-and-use-git-send-email-to-work-with-gmail-to-email-patches-to>`_.

Finally, after you have configured you email properly, you can send out a patch using:

.. code-block::

    git send-email 0001-contribute.rst-Add-git-section.patch

replacing of course the above patchfile name with whatever was your own patch.
This command will then ask you ``To whom should the emails be sent (if anyone)?``
Here, you have to write the email address of the list you want to send out the patch to.

``git send-email`` also has command line options like ``--to`` and ``--cc`` that you can also use
to add more email addresses of whoever you want to keep in CC. Generally it is a good idea to keep yourself
in CC.

.. _linux-upstream-c-programming:

C-Programming
*************

It is highly recommended that you have proficiency in C-Programming, because well the kernel is mostly
written in C! For starters, you can go through Dennis Ritchie's C Programming book to understand
the language and also solve the exercises given there for getting hands on.

.. _linux-upstream-cross-arch:

Cross-arch Development
**********************

While working with the kernel, you'll most likely not be compiling it on the machine
that you intend to actually boot it on.
For example if you are compiling the Kernel for BeageBone Black it's probably not ideal
for you to actually clone the entire kernel on BeagleBone Black and then compile it there.
What you'd do instead is pick a much powerful machine like a Desktop PC or laptop and
then use cross arch compilers like the arm-gcc for instance to compile the kernel for your
target device.

.. _linux-upstream-embedded-buses:

Basics of embedded buses (I2C, UART, SPI, etc.)
************************************************

In the world of embedded, you often need to communicate with peripherals over very low level protocols.
To name a few, I2C, UART, SPI, etc. are all serial protocols used to communicate with a variety of devices and
peripherals.

It's recommended to understand at least the basics of each of the protocol so you know what's actually going
on when you write for instance an I2C or SPI driver to communicate with let's say a sensor.

.. _linux-upstream-drivers:

Device Drivers in Embedded Systems
**********************************

I used the term "Drivers" in the above section, but what does it really mean?

.. todo::

   **Why "device" drivers?**

.. todo::

   **Why do we need drivers?**

.. todo::

   **What do drivers look like?**

.. _linux-upstream-device-trees:

Device Trees
************

We just learned about drivers, and it's time that once you have written a driver in the kernel,
you obviously want it to work! So how do we really tell the kernel which drivers to load?
How do we, at boot time, instruct which devices are present on the board you are booting on?

The kernel does not contain the description of the hardware,
it is located in a separate binary: the device tree blob.

**What is a Device Tree?**

A device tree is a tree data structure with nodes that describe
the physical devices in a system. It is used to describe system hardware. 
A boot program loads a device tree into a client program’s memory and 
passes a pointer to the device tree to the client.



.. _linux-upstream-additional-resources:

Additional Resources
********************

1. `Device Trees for Dummies PDF <https://elinux.org/images/f/f9/Petazzoni-device-tree-dummies_0.pdf>`_
2. `What are Device Drivers <https://tldp.org/LDP/tlk/dd/drivers.html>`_
3. `Submitting your patches upstream <https://www.kernel.org/doc/html/v4.17/process/submitting-patches.html>`_
