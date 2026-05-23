.. _upgrade-beaglebone-ai-software:

Upgrade BeagleBone AI software
###############################

.. important:: 
        This documentation is very old and your feedback is requested, ideally via 
        the discussion mailing-list. Otherwise, visit /about/jkridner to contact me 
        directly to provide feedback, because it is important this page be reasonably easy to use.

.. note:: 
        By default, the boards may run warm and shutdown. Please keep significant 
        ventilation on your board and update your software per these instructions.

There are 4 main steps to updating the software on BeagleBone AI:

1. Get connected to the Internet
2. Update the boot-up scripts and Linux kernel
3. Update distribution components
4. Update examples in the Cloud9 IDE workspace

The distribution components includes all of the on-board software utilizing Debian package management. 
This is the vast majority of the on-board software.

The examples in the Cloud9 IDE workspace are managed with a version control tool called git. 
This is so that it is possible to edit, record changes and revert changes to any of the examples. 
The Cloud9 IDE is integrated with this version control and history can be seen using the "Changes" tab on the far-left.

The boot-up scripts and Linux kernel updates are managed separately from rest of the system to simplified maintanence.
Get connected to the Internet

There are many ways to get BeagleBone AI onto the Internet. Ethernet, WiFi and USB-based methods are 
described below. Getting an Internet connection and performing the distribution, examples and kernel 
updates below is the fastest way to get BeagleBone AI up-to-date.
Ethernet

Just connect BeagleBone AI to your router and it will automatically DHCP an IP address for access to the Internet.

.. code-block::  console

      debian@beaglebone:/var/lib/cloud9$ ifconfig eth0
      eth0: flags=-28605  mtu 1500
              inet 192.168.0.174  netmask 255.255.255.0  broadcast 192.168.0.255
              inet6 fe80::8a3f:4aff:fe82:c102  prefixlen 64  scopeid 0x20
              ether 88:3f:4a:82:c1:02  txqueuelen 1000  (Ethernet)
              RX packets 17763  bytes 12611619 (12.0 MiB)
              RX errors 0  dropped 0  overruns 0  frame 0
              TX packets 7744  bytes 1010400 (986.7 KiB)
              TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
              device interrupt 126

      debian@beaglebone:/var/lib/cloud9$    

WiFi (without an Enterprise Login)
**********************************

Utilize the connman command-line app or the cmst graphical utility to connect to your WiFi network.

.. code-block:: console

      debian@beaglebone:/var/lib/cloud9$ sudo connmanctl
      [sudo] password for debian:temppwd
      connmanctl> scan wifi
      Scan completed for wifi
      connmanctl> services
             MyWifi                  wifi_1234567890_1234567890123456_managed_psk
      connmanctl> agent on
      Agent registered
      connmanctl> connect wifi_1234567890_1234567890123456_managed_psk⏎
      Agent RequestInput wifi_1234567890_1234567890123456_managed_psk
             Passphrase = [ Type=psk, Requirement=mandatory, Alternates=[ WPS ] ]
             WPS = [ Type=wpspin, Requirement=alternate ]
      Passphrase? MySecretPassphrase
      Connected wifi_1234567890_1234567890123456_managed_psk
      connmanctl> quit
      debian@beaglebone:/var/lib/cloud9$ ifconfig wlan0
      wlan0: flags=-28605  mtu 1500
              inet 192.168.0.193  netmask 255.255.255.0  broadcast 192.168.0.255
              inet6 fe80::82c5:f2ff:fe7f:722d  prefixlen 64  scopeid 0x20
              ether 80:c5:f2:7f:72:2d  txqueuelen 1000  (Ethernet)
              RX packets 24  bytes 2734 (2.6 KiB)
              RX errors 0  dropped 0  overruns 0  frame 0
              TX packets 56  bytes 10405 (10.1 KiB)
              TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

      debian@beaglebone:/var/lib/cloud9$

WiFi with Enterprise Login
**************************

For networks utilizing 802.1x Enterprise Login requirements, such as Eduroam, the creation of an additional configuration file can enable access.

Content taken from librobotcontrol documentation

Many wifi networks such as those found at universities and enterprises, require a user login instead of a shared passphrase. To demonstrate how to configure connman to connect to such networks, we will use the UCSD campus-wide network as an example.

Start with a normal scan and look for the desired enterprise network.

.. code-block:: console

      debian@beaglebone:/var/lib/cloud9$ sudo connmanctl
      [sudo] password for debian:temppwd
      connmanctl> scan wifi
      Scan completed for wifi
      connmanctl> services
              UCSD-PROTECTED       wifi_000f540aa884_554353442d50524f544543544544-ieee8021x
              ATT5363              wifi_ec1127bffa51_41545435333633_managed_psk
              2WIRE407             wifi_ec1127bffa51_3257495245343037_managed_psk
              ATT8fHHhfi           wifi_ec1127bffa51_41545438664848686669_managed_psk
      connmanctl> quit

Note how the type of network is listed as ieee8021x indicating that it uses Network 
Access Control instead of a typical passkey (psk) as you would find in a consumer home network.

Make a new file in the /var/lib/connman/ directory with a name matching what is listed 
during the scan. For this example, the name would be 000f540aa884_554353442d50524f544543544544-ieee8021x.config

Fill in this file as follows, replacing the service name, SSID, Identity, and Passphrase with 
your own details. Your enterprise network may also use an authentication method other than 
PEAP and MSCHAPV2. Consult the IT help desk for your enterprise for details on that configuration.

.. code-block:: console

      debian@beaglebone:/var/lib/cloud9$ sudo nano /var/lib/connman/wifi_000f540aa884_554353442d50524f544543544544-ieee8021x.config
      [sudo] password for debian:temppwd

      Enter your information into the new config file like so:

      [service_wifi_000f540aa884_554353442d50524f544543544544_managed_ieee8021x]
      Type = wifi
      SSID = 554353442d50524f544543544544
      EAP = peap
      Phase2 = MSCHAPV2
      Identity= USERNAME
      Passphrase= PASSWORD

      Restart the connman service and check if the connection was successful

      debian@beaglebone:/var/lib/cloud9$ sudo systemctl restart connman
      debian@beaglebone:/var/lib/cloud9$ ifconfig wlan0
      wlan0: flags=-28605  mtu 1500
              inet 192.168.0.193  netmask 255.255.255.0  broadcast 192.168.0.255
              inet6 fe80::82c5:f2ff:fe7f:722d  prefixlen 64  scopeid 0x20
              ether 80:c5:f2:7f:72:2d  txqueuelen 1000  (Ethernet)
              RX packets 24  bytes 2734 (2.6 KiB)
              RX errors 0  dropped 0  overruns 0  frame 0
              TX packets 56  bytes 10405 (10.1 KiB)
              TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

      debian@beaglebone:/var/lib/cloud9$

USB via Internet Connection Sharing
***********************************

You need to first establish a shell connection different than the USB network connection 
you plan on using to get to the Internet.

In your host operating system, you'll need to share your Internet connection back to the 
board. With an Ubuntu host, use the utility "nm-connection-editor".

.. code:: console

      sudo ip addr flush dev usb0

.. code:: console

      sudo dhclient usb0

Notes: How to find MAC address and correct connection?

Notes: On Ubuntu, the IPv4 Settings terminology "Shared to other computers" is what you apply to 
the connection to your board (ie., downlink) not to your Internet-connected WiFi or Ethernet (ie., uplink).
Update the boot-up scripts and Linux kernel

.. code-block:: console

      debian@beaglebone:/var/lib/cloud9$ cd /opt/scripts
      debian@beaglebone:/opt/scripts$ git pull
      Already up-to-date.
      debian@beaglebone:/opt/scripts$ sudo tools/update_kernel.sh
      [sudo] password for debian:temppwd
      info: checking archive
      2019-09-06 02:29:22 URL:https://rcn-ee.com/repos/latest/stretch-armhf/LATEST-ti [168/168] -> "LATEST-ti" [1]
      -----------------------------
      Kernel Options:
      ABI:1 LTS41 4.1.30-ti-r70
      ABI:1 LTS44 4.4.155-ti-r155
      ABI:1 LTS49 4.9.147-ti-r121
      ABI:1 LTS414 4.14.108-ti-r116
      ABI:1 LTS419 4.19.59-ti-r26
      -----------------------------
      Kernel version options:
      -----------------------------
      LTS44: --lts-4_4
      LTS49: --lts-4_9
      LTS414: --lts-4_14
      LTS419: --lts-4_19
      STABLE: --stable
      TESTING: --testing
      -----------------------------
      info: you are running: [4.14.108-ti-r113], latest is: [4.14.108-ti-r116] updating...
      Ign:1 http://deb.debian.org/debian stretch InRelease
      Get:2 http://deb.debian.org/debian stretch-updates InRelease [91.0 kB]
      .
      .
      .
      (Reading database ... 109903 files and directories currently installed.)
      Preparing to unpack .../ti-sgx-jacinto6evm-modules-4.14.108-ti-r116_1stretch_armhf.deb ...
      Unpacking ti-sgx-jacinto6evm-modules-4.14.108-ti-r116 (1stretch) ...
      Setting up ti-sgx-jacinto6evm-modules-4.14.108-ti-r116 (1stretch) ...
      update-initramfs: Generating /boot/initrd.img-4.14.108-ti-r116
      debian@beaglebone:/opt/scripts$ sudo shutdown -r now

      Update distribution components

      debian@beaglebone:/var/lib/cloud9$ sudo apt update
      [sudo] password for debian:temppwd
      Ign:1 http://deb.debian.org/debian stretch InRelease
      Hit:2 http://deb.debian.org/debian stretch-updates InRelease
      Hit:3 http://deb.debian.org/debian-security stretch/updates InRelease
      .
      .
      .
      debian@beaglebone:/var/lib/cloud9$ sudo apt upgrade
      .
      .
      .
        libnginx-mod-http-xslt-filter libnginx-mod-mail libnginx-mod-stream libpq5 linux-cpupower linux-libc-dev nginx nginx-common nginx-full tzdata
      23 upgraded, 0 newly installed, 0 to remove and 1 not upgraded.
      Need to get 10.3 MB of archives.
      After this operation, 41.0 kB of additional disk space will be used.
      Do you want to continue? [Y/n] y
      Get:1 http://deb.debian.org/debian stretch-updates/main armhf tzdata all 2019b-0+deb9u1 [275 kB]
      Get:2 http://repos.rcn-ee.com/debian stretch/main armhf bonescript armhf 0.7.3-git20190822.0-0rcnee1~stretch+20190903 [5,463 kB]
      Get:3 http://deb.debian.org/debian-security stretch/updates/main armhf libcpupower1 armhf 4.9.168-1+deb9u5 [637 kB]
      .
      .
      .
      Setting up libiio-utils (0.16-1rcnee0~stretch+20190812) ...
      Setting up libnginx-mod-http-echo (1.10.3-1+deb9u3) ...
      Setting up linux-cpupower (4.9.168-1+deb9u5) ...
      Setting up nginx-full (1.10.3-1+deb9u3) ...
      [ ok ] Upgrading binary: nginx.
      Setting up nginx (1.10.3-1+deb9u3) ...
      Processing triggers for initramfs-tools (0.130) ...
      update-initramfs: Generating /boot/initrd.img-4.14.108-ti-r116
      debian@beaglebone:/var/lib/cloud9$ sudo apt install -y ti-tidl mjpg-streamer-opencv-python

      Update examples in the Cloud9 IDE workspace

      debian@beaglebone:/var/lib/cloud9$ cd /var/lib/cloud9
      debian@beaglebone:/var/lib/cloud9$ git pull
      Already up-to-date.
      debian@beaglebone:/var/lib/cloud9$

      Test installed versions

      debian@beaglebone:/var/lib/cloud9$ sudo /opt/scripts/tools/version.sh
      [sudo] password for debian:temppwd
      git:/opt/scripts/:[5b2e16aa1e5c0f627f1d48a6dd1c13b446b9f53b]
      model:[BeagleBoard.org_BeagleBone_AI]
      dogtag:[BeagleBoard.org Debian Image 2019-08-02]
      kernel:[4.14.108-ti-r116]
      nodejs:[v6.17.0]
      pkg check: to individually upgrade run: [sudo apt install --only-upgrade ]
      pkg:[bb-cape-overlays]:[4.4.20190812.0-0rcnee0~stretch+20190812]
      pkg:[bb-wl18xx-firmware]:[1.20190227.1-0rcnee0~stretch+20190227]
      pkg:[kmod]:[23-2rcnee1~stretch+20171005]
      pkg:[librobotcontrol]:[1.0.4-git20190227.1-0rcnee0~stretch+20190327]
      pkg:[firmware-ti-connectivity]:[20180825+dfsg-1rcnee1~stretch+20181217]
      groups:[debian : debian adm kmem dialout cdrom floppy audio dip video plugdev users systemd-journal i2c bluetooth netdev gpio pwm eqep remoteproc admin spi tisdk weston-launch xenomai cloud9ide]
      cmdline:[console=ttyS0,115200n8 root=/dev/mmcblk1p1 ro rootfstype=ext4 rootwait coherent_pool=1M net.ifnames=0 rng_core.default_quality=100 quiet]
      dmesg | grep remote
      [    2.945344] remoteproc remoteproc0: 4b234000.pru is available
      [    2.946253] remoteproc remoteproc1: 4b238000.pru is available
      [    2.962679] remoteproc remoteproc2: 4b2b4000.pru is available
      [    2.965359] remoteproc remoteproc3: 4b2b8000.pru is available
      [    6.569222] remoteproc remoteproc4: 58820000.ipu is available
      [    6.598088] remoteproc remoteproc5: 55020000.ipu is available
      [    6.606271] remoteproc remoteproc6: 40800000.dsp is available
      [    6.627725] remoteproc remoteproc7: 41000000.dsp is available
      [    6.634220] remoteproc remoteproc4: powering up 58820000.ipu
      [    6.634239] remoteproc remoteproc4: Booting fw image dra7-ipu1-fw.xem4, size 6867360
      [    6.662443] remoteproc remoteproc4: registered virtio0 (type 7)
      [    6.662449] remoteproc remoteproc4: remote processor 58820000.ipu is now up
      [    6.676794] remoteproc remoteproc5: powering up 55020000.ipu
      [    6.676819] remoteproc remoteproc5: Booting fw image dra7-ipu2-fw.xem4, size 3751356
      [    6.842752] Modules linked in: omap_remoteproc virtio_rpmsg_bus rpmsg_core usb_f_ecm usb_f_mass_storage iptable_nat nf_conntrack_ipv4 nf_defrag_ipv4 nf_nat_ipv4 nf_nat nf_conntrack usb_f_rndis u_ether libcomposite iptable_mangle iptable_filter cmemk(O) uio_pdrv_genirq uio spidev pruss_soc_bus pru_rproc pruss pruss_intc ip_tables x_tables
      [    6.843887] Modules linked in: omap_remoteproc virtio_rpmsg_bus rpmsg_core usb_f_ecm usb_f_mass_storage iptable_nat nf_conntrack_ipv4 nf_defrag_ipv4 nf_nat_ipv4 nf_nat nf_conntrack usb_f_rndis u_ether libcomposite iptable_mangle iptable_filter cmemk(O) uio_pdrv_genirq uio spidev pruss_soc_bus pru_rproc pruss pruss_intc ip_tables x_tables
      [    6.849561] Modules linked in: omap_remoteproc virtio_rpmsg_bus rpmsg_core usb_f_ecm usb_f_mass_storage iptable_nat nf_conntrack_ipv4 nf_defrag_ipv4 nf_nat_ipv4 nf_nat nf_conntrack usb_f_rndis u_ether libcomposite iptable_mangle iptable_filter cmemk(O) uio_pdrv_genirq uio spidev pruss_soc_bus pru_rproc pruss pruss_intc ip_tables x_tables
      [    6.919311] remoteproc remoteproc5: registered virtio1 (type 7)
      [    6.919319] remoteproc remoteproc5: remote processor 55020000.ipu is now up
      [    6.926824] remoteproc remoteproc7: powering up 41000000.dsp
      [    6.926842] remoteproc remoteproc7: Booting fw image dra7-dsp2-fw.xe66, size 20998684
      [    6.936607] remoteproc remoteproc6: powering up 40800000.dsp
      [    6.936623] remoteproc remoteproc6: Booting fw image dra7-dsp1-fw.xe66, size 20998684
      [    7.001835] remoteproc remoteproc7: registered virtio2 (type 7)
      [    7.001842] remoteproc remoteproc7: remote processor 41000000.dsp is now up
      [    7.011099] remoteproc remoteproc6: registered virtio3 (type 7)
      [    7.011106] remoteproc remoteproc6: remote processor 40800000.dsp is now up
      dmesg | grep pru
      [    2.941572] pruss 4b200000.pruss: creating PRU cores and other child platform devices
      [    2.945344] remoteproc remoteproc0: 4b234000.pru is available
      [    2.945394] pru-rproc 4b234000.pru: PRU rproc node /ocp/pruss_soc_bus@4b226004/pruss@0/pru@34000 probed successfully
      [    2.946253] remoteproc remoteproc1: 4b238000.pru is available
      [    2.946307] pru-rproc 4b238000.pru: PRU rproc node /ocp/pruss_soc_bus@4b226004/pruss@0/pru@38000 probed successfully
      [    2.947598] pruss 4b280000.pruss: creating PRU cores and other child platform devices
      [    2.962679] remoteproc remoteproc2: 4b2b4000.pru is available
      [    2.962733] pru-rproc 4b2b4000.pru: PRU rproc node /ocp/pruss_soc_bus@4b2a6004/pruss@0/pru@34000 probed successfully
      [    2.965359] remoteproc remoteproc3: 4b2b8000.pru is available
      [    2.965409] pru-rproc 4b2b8000.pru: PRU rproc node /ocp/pruss_soc_bus@4b2a6004/pruss@0/pru@38000 probed successfully
      [    6.842752] Modules linked in: omap_remoteproc virtio_rpmsg_bus rpmsg_core usb_f_ecm usb_f_mass_storage iptable_nat nf_conntrack_ipv4 nf_defrag_ipv4 nf_nat_ipv4 nf_nat nf_conntrack usb_f_rndis u_ether libcomposite iptable_mangle iptable_filter cmemk(O) uio_pdrv_genirq uio spidev pruss_soc_bus pru_rproc pruss pruss_intc ip_tables x_tables
      [    6.843887] Modules linked in: omap_remoteproc virtio_rpmsg_bus rpmsg_core usb_f_ecm usb_f_mass_storage iptable_nat nf_conntrack_ipv4 nf_defrag_ipv4 nf_nat_ipv4 nf_nat nf_conntrack usb_f_rndis u_ether libcomposite iptable_mangle iptable_filter cmemk(O) uio_pdrv_genirq uio spidev pruss_soc_bus pru_rproc pruss pruss_intc ip_tables x_tables
      [    6.849561] Modules linked in: omap_remoteproc virtio_rpmsg_bus rpmsg_core usb_f_ecm usb_f_mass_storage iptable_nat nf_conntrack_ipv4 nf_defrag_ipv4 nf_nat_ipv4 nf_nat nf_conntrack usb_f_rndis u_ether libcomposite iptable_mangle iptable_filter cmemk(O) uio_pdrv_genirq uio spidev pruss_soc_bus pru_rproc pruss pruss_intc ip_tables x_tables
      [    9.175815] pruss_uio_shmem 4b200000.pruss_shmem: Allocating gdev
      [    9.175825] pruss_uio_shmem 4b200000.pruss_shmem: Allocating info
      [    9.175832] pruss_uio_shmem 4b200000.pruss_shmem: Requesting resource
      [    9.175853] pruss_uio_shmem 4b200000.pruss_shmem: Mapping resource
      [    9.179197] pruss_uio_shmem 4b200000.pruss_shmem: Registering with uio driver
      [    9.179745] pruss_uio_shmem 4b200000.pruss_shmem: Saving platform data
      [    9.179858] pruss_uio_shmem 4b280000.pruss_shmem: Allocating gdev
      [    9.179864] pruss_uio_shmem 4b280000.pruss_shmem: Allocating info
      [    9.179870] pruss_uio_shmem 4b280000.pruss_shmem: Requesting resource
      [    9.179886] pruss_uio_shmem 4b280000.pruss_shmem: Mapping resource
      [    9.179899] pruss_uio_shmem 4b280000.pruss_shmem: Registering with uio driver
      [    9.180137] pruss_uio_shmem 4b280000.pruss_shmem: Saving platform data
      dmesg | grep pinctrl-single
      [    0.914771] pinctrl-single 4a003400.pinmux: 282 pins at pa fc003400 size 1128
      dmesg | grep gpio-of-helper
      lsusb
      Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
      Bus 001 Device 002: ID 046d:0825 Logitech, Inc. Webcam C270
      Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
      END
      debian@beaglebone:/var/lib/cloud9$
