.. _pru-cookbook-more:

More Performance
##################

So far in all our examples we've been able to meet our timing goals by writing
our code in the C programming language. The C compiler does a surprisingly
good job at generating code, most the time.  However there are times
when very precise timing is needed and the compiler isn't doing it.

At these times you need to write in assembly language.  This chapter
introduces the PRU assembler and shows how to call assembly code from
C. Detailing on how to program in assembly are beyond the scope of this text.

The following are resources used in this chapter.

.. note::

   *Resources*

   * `PRU Optimizing C/C++ Compiler, v2.2, User's Guide <http://www.ti.com/lit/ug/spruhv7b/spruhv7b.pdf>`_
   * `PRU Assembly Language Tools User's Guide <http://www.ti.com/lit/ug/spruhv6b/spruhv6b.pdf>`_
   * `PRU Assembly Instruction User Guide <http://www.ti.com/lit/ug/spruij2/spruij2.pdf>`_

Calling Assembly from C
************************

Problem
--------

You have some C code and you want to call an assembly language routine from it.

Solution
---------

You need to do two things, write the assembler file and modify the ``Makefile``
to include it. For example, let's write our own ``my_delay_cycles`` routine in
in assembly.  The intrinsic ``pass:[__]delay_cycles`` must be passed a compile time
constant.  Our new ``delay_cycles`` can take a runtime delay value.

:ref:`more_delay-test` is much like our other c code, but on line 10 we declare 
``my_delay_cycles`` and then on lines 24 and 26 we'll call it with an argument of 1.

.. _more_delay-test:

.. literalinclude:: ../code/07more/delay-test.pru0.c
   :caption: delay-test.pru0.c
   :linenos:

:download:`delay-test.pru0.c <../code/07more/delay-test.pru0.c>`

:ref:`more_delay` is the assembly code.

.. _more_delay:

.. literalinclude:: ../code/07more/delay.pru0.asm
   :caption: delay.pru0.asm
   :linenos:

:download:`delay.pru0.asm <../code/07more/delay.pru0.asm>`

The ``Makefile`` has one addition that needs to be made to compile both :ref:`more_delay-test`
and :ref:`more_delay`. If you look in the local ``Makefile`` you'll see:

.. _more_makefile:

.. literalinclude:: ../code/07more/Makefile
   :caption: Makefile
   :linenos:

:download:`Makefile <../code/07more/Makefile>`

This Makefle includes a common Makefile at  ``/opt/source/pru-cookbook-code/common/Makefile``, this the Makefile 
you need to edit. Edit ``/opt/source/pru-cookbook-code/common/Makefile`` and go to line 195.

.. code-block:: shell-session

  $(GEN_DIR)/%.out: $(GEN_DIR)/%.o *$(GEN_DIR)/$(TARGETasm).o*
    @mkdir -p $(GEN_DIR)
    @echo 'LD	$^'
    $(eval $(call target-to-proc,$@))
    $(eval $(call proc-to-build-vars,$@))
    @$(LD) $@ $^ $(LDFLAGS) 

Add ``*(GEN_DIR)/$(TARGETasm).o*`` as shown in bold above.  You will want to remove
this addition once you are done with this example since it will break the other examples.

The following will compile and run everything.

.. code-block:: shell-session

  bone$ config-pin P9_31 pruout
  bone$ make TARGET=delay-test.pru0 TARGETasm=delay.pru0
  /opt/source/pru-cookbook-code/common/Makefile:29: MODEL=TI_AM335x_BeagleBone_Black,TARGET=delay-test.pru0
  -    Stopping PRU 0
  -	copying firmware file /tmp/vsx-examples/delay-test.pru0.out to /lib/firmware/am335x-pru0-fw
  write_init_pins.sh
  -    Starting PRU 0
  MODEL   = TI_AM335x_BeagleBone_Black
  PROC    = pru
  PRUN    = 0
  PRU_DIR = /sys/class/remoteproc/remoteproc1

The resulting output is shown in :ref:`more_my_delay_cycles`.

.. _more_my_delay_cycles:

.. figure:: figures/my_delay_cycles.png
  :align: center
  :alt: Output of my_delay_cycles()

  Output of my_delay_cycles()

Notice the on time is about 35ns and the off time is 30ns.

Discission
-----------

There is much to explain here.  Let's start with :ref:`more_delay`.

.. table:: Line-by-line of delay.pru0.asm

  +-------+-------------------------------------------------------------------------------------------------------+
  |Line   | Explanation                                                                                           |
  +=======+=======================================================================================================+
  |3      | Declare `my_delay_cycles` to be global so the linker can find it.                                     |
  +-------+-------------------------------------------------------------------------------------------------------+
  |4      | Label the starting point for `my_delay_cycles`.                                                       |
  +-------+-------------------------------------------------------------------------------------------------------+
  |5      | Label for our delay loop.                                                                             |
  +-------+-------------------------------------------------------------------------------------------------------+
  |6      | The first argument is passed in register ``r14``.  Page 111 of                                        |
  |       | `PRU Optimizing C/C++ Compiler, v2.2, User's Guide <http://www.ti.com/lit/ug/spruhv7b/spruhv7b.pdf>`_ |
  |       | gives the argument passing convention.  Registers ``r14`` to ``r29`` are used                         |
  |       | to pass arguments, if there are more arguments, the argument stack (``r4``)                           |
  |       | is used.  The other register conventions are found on page 108.                                       |
  |       | Here we subtract 1 from ``r14`` and save it back into ``r14``.                                        |
  +-------+-------------------------------------------------------------------------------------------------------+
  |7      | `qbne` is a quick branch if not equal.                                                                |
  +-------+-------------------------------------------------------------------------------------------------------+
  |9      | Once we've delayed enough we drop through the quick branch and                                        |
  |       | hit the jump.  The upper bits of register `r3` has the return address,                                |
  |       | therefore we return to the c code.                                                                    |
  +-------+-------------------------------------------------------------------------------------------------------+

:ref:`more_my_delay_cycles` shows the **on** time is 35ns and the off time is 30ns.
With 5ns/cycle this gives 7 cycles on and 6 off. These times make sense 
because each instruction takes a cycle and you have, set ``R30``, jump to
``my_delay_cycles``, ``sub``, ``qbne``, ``jmp``. Plus the instruction (not seen) that
initializes `r14` to the passed value.  That's a total of six instructions.
The extra instruction is the branch at the bottom of the ``while`` loop.


Returning a Value from Assembly
********************************

Problem
--------

Your assembly code needs to return a value.

Solution
--------

``R14`` is how the return value is passed back.  :ref:`more_test2` shows the c code.

.. _more_test2:

.. literalinclude:: ../code/07more/delay-test2.pru0.c
   :caption: delay-test2.pru0.c
   :linenos:

:download:`delay-test2.pru0.c <../code/07more/delay-test2.pru0.c>`

:ref:`more_delay2` is the assembly code.

.. _more_delay2:

.. literalinclude:: ../code/07more/delay2.pru0.asm
   :caption: delay2.pru0.asm
   :linenos:

:download:`delay2.pru0.asm <../code/07more/delay2.pru0.asm>`

An additional feature is shown in line 4 of :ref:`more_delay2`.  The
``.cdecls "delay-test2.pru0.c"`` says to include any defines from ``delay-test2.pru0.c``
In this example, line 6 of :ref:`more_test2` `#defines` TEST and line 12 of 
:ref:`more_delay2` reference it.


Using the Built-In Counter for Timing
***************************************

Problem
--------

I want to count how many cycles my routine takes.

Solution
---------

Each PRU has a ``CYCLE`` register which counts the number of cycles since
the PRU was enabled. They also have a ``STALL`` register that counts how
many times the PRU stalled fetching an instruction.
:ref:`more_cycle` shows they are used.

.. _more_cycle:

.. literalinclude:: ../code/07more/cycle.pru0.c
   :caption: cycle.pru0.c - Code to count cycles.
   :linenos:

:download:`cycle.pru0.c <../code/07more/cycle.pru0.c>`

Discission
------------

The code is mostly the same as other examples. ``cycle`` and ``stall`` end up in registers which
we can read using prudebug. :ref:`more_cycle_lines` is the Line-by-line.

.. _more_cycle_lines:

.. table:: Line-by-line for cycle.pru0.c

  +-------+---------------------------------------------------------------------------------------+
  |Line   | Explanation                                                                           |
  +=======+=======================================================================================+
  |4      | Include needed to reference `CYCLE` and `STALL`.                                      |
  +-------+---------------------------------------------------------------------------------------+
  |16     | Declaring `cycle` and `stall`.  The compiler will optimize these and just             |
  |       | keep them in registers.  We'll have to look at the `cycle.pru0.lst` file to see where |
  |       | they are stored.                                                                      |
  +-------+---------------------------------------------------------------------------------------+
  |21     | Enables `CYCLE`.                                                                      |
  +-------+---------------------------------------------------------------------------------------+
  |26     | Reset `CYCLE`. It ignores the value assigned to it and always sets it                 |
  |       | to 0.  `cycle` is on the right hand side to make the compiler give it its own         |
  |       | register.                                                                             |
  +-------+---------------------------------------------------------------------------------------+
  |28, 29 | Reads the `CYCLE` and `STALL` values into registers.                                  |
  +-------+---------------------------------------------------------------------------------------+

You can see where ``cycle`` and ``stall`` are stored by looking into :ref:`more_cycle_list0`.

.. _more_cycle_list0:

.. literalinclude:: ../code/07more/cycle.pru0.lst
   :caption: /tmp/vsx-examples/cycle.pru0.lst Lines 113..119
   :lines: 113-119
   :lineno-start: 113
   :linenos:

:download:`cycle.pru0.lst <../code/07more/cycle.pru0.lst>`

Here the ``LDI32`` instruction loads the address ``0x22000`` into ``r0``. This is the offset to 
the ``CTRL`` registers. Later in the file we see :ref:`more_cycle_list1`.
 
.. _more_cycle_list1:

.. literalinclude:: ../code/07more/cycle.pru0.lst
   :caption: /tmp/vsx-examples/cycle.pru0.lst Lines 146..152
   :lines: 146-152
   :lineno-start: 146
   :linenos:

:download:`cycle.pru0.lst <../code/07more/cycle.pru0.lst>`


The first ``LBBO`` takes the contents of ``r0`` and adds the offset 12 to it and copies 4 bytes 
into ``r1``.  This points to ``CYCLE``, so ``r1`` has the contents of ``CYCLE``.

The second ``LBBO`` does the same, but with offset 16, which points to ``STALL``,
thus ``STALL`` is now  in ``r0``.

Now fire up **prudebug** and look at those registers. 

.. code-block:: shell-session

  bone$ sudo prudebug
  PRU0> r
  r
  r
  Register info for PRU0
      Control register: 0x00000009
        Reset PC:0x0000  STOPPED, FREE_RUN, COUNTER_ENABLED, NOT_SLEEPING, PROC_DISABLED

      Program counter: 0x0012
        Current instruction: HALT

      R00: *0x00000005*    R08: 0x00000200    R16: 0x000003c6    R24: 0x00110210
      R01: *0x00000003*    R09: 0x00000000    R17: 0x00000000    R25: 0x00000000
      R02: 0x000000fc    R10: 0xfff4ea57    R18: 0x000003e6    R26: 0x6e616843
      R03: 0x0004272c    R11: 0x5fac6373    R19: 0x30203020    R27: 0x206c656e
      R04: 0xffffffff    R12: 0x59bfeafc    R20: 0x0000000a    R28: 0x00003033
      R05: 0x00000007    R13: 0xa4c19eaf    R21: 0x00757270    R29: 0x02100000
      R06: 0xefd30a00    R14: 0x00000005    R22: 0x0000001e    R30: 0xa03f9990
      R07: 0x00020024    R15: 0x00000003    R23: 0x00000000    R31: 0x00000000
  

So ``cycle`` is 3 and ``stall`` is 5. It must be one cycle to clear the GPIO and 2 cycles to read the 
``CYCLE`` register and save it in the register. It's interesting there are 5 ``stall`` cycles. 

If you switch the order of lines 30 and 31 you'll see ``cycle`` is 7 and ``stall`` is 2. ``cycle`` now includes the 
time needed to read ``stall`` and ``stall`` no longer includes the time to read ``cycle``.

Xout and Xin - Transferring Between PRUs
*****************************************

Problem
--------

I need to transfer data between PRUs quickly.

Solution
---------

The ``pass:[__]xout()`` and ``pass:[__]xin()`` intrinsics are able to transfer up to 30 registers between PRU 0 and PRU 1 quickly. 
:ref:`more_xout` shows how ``xout()`` running on PRU 0 transfers six registers to PRU 1.

.. _more_xout:

.. literalinclude:: ../code/07more/xout.pru0.c
   :caption: xout.pru0.c
   :linenos:

:download:`xout.pru0.c <../code/07more/xout.pru0.c>`

PRU 1 waits at line 41 until PRU 0 signals it.  :ref:`more_xin` sends an
interrupt to PRU 0 and waits for it to send the data.

.. _more_xin:

.. literalinclude:: ../code/07more/xin.pru1.c
   :caption: xin.pru1.c
   :linenos:

:download:`xin.pru1.c <../code/07more/xin.pru1.c>`

Use ``prudebug`` to see registers R5-R10 are transferred from PRU 0 to PRU 1.

.. code-block:: shell-session

  PRU0> r
  Register info for PRU0
      Control register: 0x00000001
        Reset PC:0x0000  STOPPED, FREE_RUN, COUNTER_DISABLED, NOT_SLEEPING, PROC_DISABLED

      Program counter: 0x0026
        Current instruction: HALT

      R00: 0x00000012    *R08: 0xbbbbbbbb*    R16: 0x000003c6    R24: 0x00110210
      R01: 0x00020000    *R09: 0x87654321*    R17: 0x00000000    R25: 0x00000000
      R02: 0x000000e4    *R10: 0xcccccccc*    R18: 0x000003e6    R26: 0x6e616843
      R03: 0x0004272c    R11: 0x5fac6373    R19: 0x30203020    R27: 0x206c656e
      R04: 0xffffffff    R12: 0x59bfeafc    R20: 0x0000000a    R28: 0x00003033
      *R05: 0xdeadbeef*    R13: 0xa4c19eaf    R21: 0x00757270    R29: 0x02100000
      *R06: 0xaaaaaaaa*    R14: 0x00000005    R22: 0x0000001e    R30: 0xa03f9990
      *R07: 0x12345678*    R15: 0x00000003    R23: 0x00000000    R31: 0x00000000

  PRU0> *pru 1*
  pru 1
  Active PRU is PRU1.

  PRU1> *r*
  r
  Register info for PRU1
      Control register: 0x00000001
        Reset PC:0x0000  STOPPED, FREE_RUN, COUNTER_DISABLED, NOT_SLEEPING, PROC_DISABLED

      Program counter: 0x000b
        Current instruction: HALT

      R00: 0x00000100    *R08: 0xbbbbbbbb*    R16: 0xe9da228b    R24: 0x28113189
      R01: 0xe48cdb1f    *R09: 0x87654321*    R17: 0x66621777    R25: 0xddd29ab1
      R02: 0x000000e4    *R10: 0xcccccccc*    R18: 0x661f83ea    R26: 0xcf1cd4a5
      R03: 0x0004db97    R11: 0xdec387d5    R19: 0xa85adb78    R27: 0x70af2d02
      R04: 0xa90e496f    R12: 0xbeac3878    R20: 0x048fff22    R28: 0x7465f5f0
      *R05: 0xdeadbeef*    R13: 0x5777b488    R21: 0xa32977c7    R29: 0xae96b530
      *R06: 0xaaaaaaaa*    R14: 0xffa60550    R22: 0x99fb123e    R30: 0x52c42a0d
      *R07: 0x12345678*    R15: 0xdeb2142d    R23: 0xa353129d    R31: 0x00000000


Discussion
-----------

:ref:`more_zout_lines` shows the line-by-line for ``xout.pru0.c``

.. _more_zout_lines:

.. table:: xout.pru0.c Line-by-line

  +-------+---------------------------------------------------------------------------------------------------------+
  |Line   | Explanation                                                                                             |
  +=======+=========================================================================================================+
  |4      | A different resource so PRU 0 can receive a signal from PRU 1.                                          |
  +-------+---------------------------------------------------------------------------------------------------------+
  |9-16   | ``dmemBuf`` holds the data to be sent to PRU 1.  Each will be transferred                               |
  |       | to its corresponding register by ``xout()``.                                                            |
  +-------+---------------------------------------------------------------------------------------------------------+
  |21-22  | Define the interrupts we're using.                                                                      |
  +-------+---------------------------------------------------------------------------------------------------------+
  |27-28  | Clear the interrupts.                                                                                   |
  +-------+---------------------------------------------------------------------------------------------------------+
  |31-36  | Initialize dmemBuf with easy to recognize values.                                                       |
  +-------+---------------------------------------------------------------------------------------------------------+
  |40     | Wait for PRU 1 to signal.                                                                               |
  +-------+---------------------------------------------------------------------------------------------------------+
  |45     | ``pass:[__]xout()`` does a direct transfer to PRU 1. Page 92 of                                         |
  |       | `PRU Optimizing C/C++ Compiler, v2.2, User's Guide <http://www.ti.com/lit/ug/spruhv7b/spruhv7b.pdf>`_   | 
  |       | shows how to use `xout()`. The first argument, 14, says to do a direct transfer to PRU 1.  If the       |
  |       | first argument is 10, 11 or 12, the data is transferred to one of three scratchpad memories that        |
  |       | PRU 1 can access later. The second argument, 5, says to start transferring with register ``r5``         |
  |       | and use as many registers as needed to transfer all of ``dmemBuf``. The third argument, 0,              |
  |       | says to not use remapping. (See the User's Guide for details.)                                          |
  |       | The final argument is the data to be transferred.                                                       |
  +-------+---------------------------------------------------------------------------------------------------------+
  |48     | Clear the interrupt so it can go again.                                                                 |
  +-------+---------------------------------------------------------------------------------------------------------+

:ref:`more_xin_lines` shows the line-by-line for ``xin.pru1.c``.

.. _more_xin_lines:

.. table:: xin.pru1.c Line-by-line

  +-------+-----------------------------------------------------------+
  |Line   | Explanation                                               |
  +=======+===========================================================+
  |8-15   | Place to put the received data.                           |
  +-------+-----------------------------------------------------------+
  |26     | Signal PRU 0                                              |
  +-------+-----------------------------------------------------------+
  |30     | Receive the data. The arguments are the same as `xout()`, |
  |       | 14 says to get the data directly from PRU 0.              |
  |       | 5 says to start with register `r5`.                       |
  |       | `dmemBuf` is where to put the data.                       |
  +-------+-----------------------------------------------------------+

If you really need speed, considering using ``pass:[__]xout()`` and ``pass:[__]xin()`` in assembly.

Copyright
==========

.. literalinclude:: ../code/07more/copyright.c
   :caption: copyright.c
   :linenos:

:download:`copyright.c <../code/07more/copyright.c>`
