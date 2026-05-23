.. _intro-riscv:

Introduction to RISC-V
######################

`RISC-V`_ is an open standard `instruction set architecture (ISA) <ISA>`_, meaning that the details of the standard are publicly available and free
to license. Companies that make `CPUs`_ that utilize the RISC-V ISA are able to do so in a compatible way without paying royalty.

Why RISC-V?
***********

.. figure:: figures/why-riscv.png

   Why RISC-V?

There are many benefits, but one that stands out is the opportunity for diversity. CPU vendors are able to create custom
CPUs with performance and features suited for various applications, making their own power, performance and cost tradeoffs,
while still maintaining compatibility. The ability to run tens of thousands of pre-built binary packages in a Linux
distribution is just an example.

Hardware
********

Check out :ref:`beaglev-fire-home` and :ref:`beaglev-ahead-home` for suitable hardware for learning more about RISC-V.

Hello World
***********

Stephen Smith wrote a great `RISC-V Assembly Language Hello World blog post <https://smist08.wordpress.com/2019/09/07/risc-v-assembly-language-hello-world/>`_ that
runs well on BeagleV boards.

hello.s
=======

Once you've logged into your BeagleV, save the :ref:`hello.s <hello_s_source>` file.

.. _hello_s_source:

.. literalinclude:: code/hello.s
    :language: asm
    :caption: hello.s
    :linenos:

:download:`hello.s<code/hello.s>`

Running hello.s
===============

Then, you can assemble, link and run :ref:`hello.s <hello_s_source>`.

.. code-block:: shell-session

  beagle@BeagleV:~$ as hello.s -o hello.o
  beagle@BeagleV:~$ ld hello.o -o hello
  beagle@BeagleV:~$ ./hello
  Hello World!


If you are curious, you can take a better look at what the executable has in it using :ref:`objdump <objdump-example>`.

.. _objdump-example:

.. code-block:: shell-session

  beagle@BeagleV:~$ objdump -d hello
  hello: 	file format elf64-littleriscv

  Disassembly of section .text:

  00000000000100e8 <_start>:
     100e8:    00100513   li    a0,1
     100ec:    00001597   auipc    a1,0x1
     100f0:    02058593   add    a1,a1,32 # 1110c <__DATA_BEGIN__>
     100f4:    00d00613   li    a2,13
     100f8:    04000893   li    a7,64
     100fc:    00000073   ecall
     10100:    00000513   li    a0,0
     10104:    05d00893   li    a7,93
     10108:    00000073   ecall

Recommended Resources
*********************

* `RISC-V Assembly Manual <https://github.com/riscv-non-isa/riscv-asm-manual/blob/master/riscv-asm.md>`_
* `Digikey Webinar on BeagleV-Fire <https://www.beagleboard.org/blog/2024-03-13-webinar-on-beaglev-fire-powered-by-polarfire-soc-risc-v-and-fpga>`_

.. _RISC-V:
   https://en.wikipedia.org/wiki/RISC-V

.. _ISA:
   https://en.wikipedia.org/wiki/Instruction_set_architecture>

.. _CPUs:
   https://en.wikipedia.org/wiki/Central_processing_unit
