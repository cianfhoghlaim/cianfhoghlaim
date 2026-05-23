.. _beagleplay-understanding-boot:

Understanding Boot
##################

There are several phases to BeaglePlay boot. The simplest place to take control of
the system is using :ref:`play-distro-boot`. It is simplest because it is very generic,
not at all specific to BeaglePlay or AM62, and was included in the earliest BeagleBoard.org Debian
images shipping pre-installed in the on-board flash.

.. _play-distro-boot:

Distro Boot
***********

For some background on distro boot, see `the u-boot documentation on
distro boot <https://docs.u-boot.org/en/latest/develop/distro.html>`_. There is
also `BeaglePlay specific u-boot documentation <https://docs.u-boot.org/en/latest/board/beagle/am62x_beagleplay.html>`_.

In :ref:`play-typical-extlinux-conf`, you can see line 1 provides a label
and subsequent indented lines provide parameters for that boot option.

.. _play-typical-extlinux-conf:

.. code-block::
    :caption: Typical /boot/firmware/extlinux/extlinux.conf file
    :linenos:

    label Linux eMMC
        kernel /Image
        append root=/dev/mmcblk0p2 ro rootfstype=ext4 rootwait net.ifnames=0 quiet
        fdtdir /
        #fdtoverlays /overlays/<file>.dtbo
        initrd /initrd.img

It is important to note that this file is not on the root file system of BeaglePlay. It
is sitting on a separate FAT32 partition that is mounted at ``/boot/firmware``. You can
see the mounted file systems and their formats in :ref:`play-boot-mounted-fs`.

The FAT32 partition in this setup is often referred to as the boot file system.

.. _play-boot-mounted-fs:

.. code-block:: shell-session
    :caption: List of mounted file systems

    debian@BeaglePlay:~$ df
    Filesystem     1K-blocks     Used Available Use% Mounted on
    udev              903276        0    903276   0% /dev
    tmpfs             197324     1524    195800   1% /run
    /dev/mmcblk0p2  14833640 12144024   1914296  87% /
    tmpfs             986608        0    986608   0% /dev/shm
    tmpfs               5120        4      5116   1% /run/lock
    /dev/mmcblk0p1    130798    53214     77584  41% /boot/firmware
    tmpfs             197320       32    197288   1% /run/user/1000
    debian@BeaglePlay:~$ lsblk
    NAME         MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
    mmcblk0      179:0    0 14.6G  0 disk 
    ├─mmcblk0p1  179:1    0  128M  0 part /boot/firmware
    └─mmcblk0p2  179:2    0 14.5G  0 part /
    mmcblk0boot0 179:256  0    4M  1 disk 
    mmcblk0boot1 179:512  0    4M  1 disk 
    debian@BeaglePlay:~$ sudo sfdisk -l /dev/mmcblk0
    Disk /dev/mmcblk0: 14.6 GiB, 15678308352 bytes, 30621696 sectors
    Units: sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disklabel type: dos
    Disk identifier: 0xba67172a

    Device         Boot  Start      End  Sectors  Size Id Type
    /dev/mmcblk0p1 *      2048   264191   262144  128M  c W95 FAT32 (LBA)
    /dev/mmcblk0p2      264192 30621695 30357504 14.5G 83 Linux


To better understand BeaglePlay's U-Boot Distro Boot, let's install a Linux kernel and
initramfs from the `Buildroot project <http://buildroot.org/>`_. There is a pre-built image
release at https://git.beagleboard.org/beagleboard/buildroot/-/releases/2023.11-beagle1.

Currently, the Linux kernel image needs to be uncompressed and stored in the FAT32 file
system. An initramfs image is a simple way to provide a starting root file system. When
running Linux, some kind of root file system is required.

An initramfs image is utilized on Debian systems to make sure any kernel modules needed are
available and to provide a bit of a recovery opportunity in case the root file system is
corrupted. You can learn more about initramfs and initrd on `the Debian Initrd Wiki
page <https://wiki.debian.org/Initrd>` and `the Linux kernel documentation admin
guide initrd entry <https://docs.kernel.org/admin-guide/initrd.html>`.

In the case of utilizing Buildroot, the
entire `Linux distribution <https://en.wikipedia.org/wiki/Linux_distribution>`_ is
incorporated into the initramfs root file system image.

The contents of the initrd can be read using ``lsinitramfs /boot/firmware/initrd.img``.

.. _play-copy-kernel:

.. code-block:: shell-session
    :caption: Copy kernel to FAT32 filesystem

    debian@BeaglePlay:~$ wget https://git.beagleboard.org/beagleboard/buildroot/-/jobs/19194/artifacts/raw/public/beagleplay/images/Image
    --2023-12-19 22:17:54--  https://git.beagleboard.org/beagleboard/buildroot/-/jobs/19194/artifacts/raw/public/beagleplay/images/Image
    Resolving git.beagleboard.org (git.beagleboard.org)... 44.226.162.25
    Connecting to git.beagleboard.org (git.beagleboard.org)|44.226.162.25|:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 32172544 (31M) [application/octet-stream]
    Saving to: ‘Image’

    Image               100%[===================>]  30.68M  1.78MB/s    in 18s     

    2023-12-19 22:18:13 (1.74 MB/s) - ‘Image’ saved [32172544/32172544]

    debian@BeaglePlay:~$ sudo cp Image /boot/firmware/Image-buildroot
    [sudo] password for debian:
    debian@BeaglePlay:~$ wget https://git.beagleboard.org/beagleboard/buildroot/-/jobs/19194/artifacts/raw/public/beagleplay/images/rootfs.cpio.gz
    --2023-12-19 22:16:44--  https://git.beagleboard.org/beagleboard/buildroot/-/jobs/19194/artifacts/raw/public/beagleplay/images/rootfs.cpio.gz
    Resolving git.beagleboard.org (git.beagleboard.org)... 44.226.162.25
    Connecting to git.beagleboard.org (git.beagleboard.org)|44.226.162.25|:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 30111086 (29M) [application/octet-stream]
    Saving to: ‘rootfs.cpio.gz’

    rootfs.cpio.gz      100%[===================>]  28.72M  21.5MB/s    in 1.3s    

    2023-12-19 22:16:46 (21.5 MB/s) - ‘rootfs.cpio.gz’ saved [30111086/30111086]

    debian@BeaglePlay:~$ sudo cp rootfs.cpio.gz /boot/firmware/rootfs.cpio.gz-buildroot

.. _play-modified-extlinux-conf:

.. code-block::
    :caption: Modified /boot/firmware/extlinux/extlinux.conf file
    :linenos:

    menu title Select image to boot
    timeout 10
    default Buildroot

    label Debian
        kernel /Image
        append root=/dev/mmcblk0p2 ro rootfstype=ext4 rootwait net.ifnames=0 quiet
        fdtdir /
        #fdtoverlays /overlays/<file>.dtbo
        initrd /initrd.img

    label Buildroot
        kernel /Image-buildroot
        append rootwait net.ifnames=0 quiet
        fdtdir /
        initrd /rootfs.cpio.gz-buildroot

.. _play-boot-modified-kernel:

.. code-block:: shell-session
    :caption: Reboot into modified kernel and rootfs

    debian@BeaglePlay:~$ sudo shutdown -r now
    Connection to 192.168.0.117 closed by remote host.
    Connection to 192.168.0.117 closed.
    jkridner@slotcar:~$ sudo nmap -n -p 22 192.168.0.0/24
    Starting Nmap 7.94SVN ( https://nmap.org ) at 2023-12-19 17:32 EST
    ...
    PORT   STATE SERVICE
    22/tcp open  ssh
    MAC Address: 50:3E:AA:AD:78:06 (TP-Link Technologies)

    Nmap scan report for 192.168.0.112
    Host is up (0.00020s latency).
    ...
    jkridner@slotcar:~$ ssh root@192.168.0.112
    The authenticity of host '192.168.0.112 (192.168.0.112)' can't be established.
    ED25519 key fingerprint is SHA256:EZdvLkCNMyhy4RhvseUSC5EwaJR5Kgpk8JZG9kF+pmk.
    This key is not known by any other names.
    Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
    Warning: Permanently added '192.168.0.112' (ED25519) to the list of known hosts.
    root@192.168.0.112's password: 
    # uname -a
    Linux BeaglePlay 6.6.3 #1 SMP Tue Dec 19 21:32:06 UTC 2023 aarch64 GNU/Linux
    # cat /etc/os-release 
    NAME=Buildroot
    VERSION=2023.11-beagle1
    ID=buildroot
    VERSION_ID=2023.11
    PRETTY_NAME="Buildroot 2023.11"


Booting U-Boot
**************

.. _play-boot-install-emmc:

.. literalinclude:: boot/install-emmc.sh
    :caption: Install bootloader to eMMC
    :language: bash

:download:`install-emmc.sh <boot/install-emmc.sh>`

