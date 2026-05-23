.. _intro-linux:

Introduction to Linux
#####################

This article seeks to give you some quick exploration of Linux. For a deeper training,
scroll down to :ref:`embedded-linux-training`.

Linux is designed to make the details of the hardware it is running on not matter so much
to users. It gives you a *somewhat* common experience on any hardware.

It also goes a bit further, providing some description of the harware as part of the running
"file system".

Typical Command-line Utilities
******************************

Most of what a new user experiences with Linux is the command-line.

.. table:: Typical Linux commands

    +---------+--------------------------------+---------+------------------------------------+
    | command | function                       | command | function                           |
    +=========+================================+=========+====================================+
    | pwd     | *show current directory*       | echo    | *print/dump value*                 |
    +---------+--------------------------------+---------+------------------------------------+
    | cd      | *change current directory*     | env     | *dump environment variables*       |
    +---------+--------------------------------+---------+------------------------------------+
    | ls      | *list directory contents*      | export  | *set environment variable*         |
    +---------+--------------------------------+---------+------------------------------------+
    | chmod   | *change file permissions*      | history | *dump command history*             |
    +---------+--------------------------------+---------+------------------------------------+
    | cp      | *copy files*                   | man     | *get help on command*              |
    +---------+--------------------------------+---------+------------------------------------+
    | mv      | *move files*                   | apropos | *show list of man pages*           |
    +---------+--------------------------------+---------+------------------------------------+
    | rm      | *remove files*                 | find    | *search for files*                 |
    +---------+--------------------------------+---------+------------------------------------+
    | mkdir   | *make directory*               | tar     | *create/extract file archives*     |
    +---------+--------------------------------+---------+------------------------------------+
    | rmdir   | *remove directory*             | gzip    | *compress a file*                  |
    +---------+--------------------------------+---------+------------------------------------+
    | cat     | *dump file contents*           | gunzip  | *decompress a file*                |
    +---------+--------------------------------+---------+------------------------------------+
    | less    | *progressively dump file*      | du      | *show disk usage*                  |
    +---------+--------------------------------+---------+------------------------------------+
    | vi      | *edit file (complex)*          | df      | *show disk free space*             |
    +---------+--------------------------------+---------+------------------------------------+
    | nano    | *edit file (simple)*           | mount   | *mount disks*                      |
    +---------+--------------------------------+---------+------------------------------------+
    | head    | *trim dump to top*             | tee     | *write dump to file in parallel*   |
    +---------+--------------------------------+---------+------------------------------------+
    | tail    | *trim dump to bottom*          | hexdump | *readable binary dumps*            |
    +---------+--------------------------------+---------+------------------------------------+

Kernel.org Documentation
************************

See https://www.kernel.org/doc.

Linux Standard Base
*******************

See https://refspecs.linuxfoundation.org/lsb.shtml.

.. code-block:: shell-session

   $ lsb_release -a

Filesystem Hierarchy Standard
*****************************

See https://www.pathname.com/fhs/

Kernel Application Binary Interface
***********************************

See https://www.kernel.org/doc/Documentation/ABI/.

Busybox
*******

Even though large distros like Debian and Ubuntu do not make extensive use of `busybox`, it is still very useful to
learn 

See http://www.busybox.net/.

.. _writing-kernel-modules:

Kernel Modules
**************

Writing a bit of code that runs in the kernel is not too difficult.

See :ref:`beagleplay-kernel-development`.

.. _embedded-linux-training:

Training
********

To continue learning more about Linux, we highly recommend https://bootlin.com/training/embedded-linux/.
