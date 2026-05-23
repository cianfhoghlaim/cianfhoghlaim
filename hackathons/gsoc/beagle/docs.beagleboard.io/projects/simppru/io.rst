IO Functions
============

-  All Header pins are ``constant integer variable`` by default, with
   its value equal to respective R30/R31 register bit

   -  Example: ``P1_20`` is an constant integer variable with value
      ``16``, similarly ``P1_02`` is an constant integer variable with
      value ``9``

Digital Write
-------------

``digital_write`` is a function which enables PRU to write given logic
level at specified output pin. It is a function with void return type
and it's parameters are ``integer`` and ``boolean``, first parameter is
the pin number to write to or PRU R30 register bit and second parameter
is ``boolean`` value to be written. ``true`` for HIGH and ``false`` for
LOW.

Syntax
~~~~~~

``digital_write(pin_number, value);``

Parameters
^^^^^^^^^^

-  ``pin_number`` is an integer. It must be a header pin name which
   supports output, or PRU R30 Register bit.
-  ``value`` is a boolean. It is used to set logic level of the output
   pin, ``true`` for HIGH and ``false`` for LOW.

Return Type
^^^^^^^^^^^

-  ``void`` - returns nothing.

Example
~~~~~~~

.. code:: python

   int a := 32;

   if : a < 32 {
       digital_write(P1_29, true);
   }
   else {
       digital_write(P1_29, false);
   }

If the value of a < 32, then pin ``P1_29`` is set to ``HIGH`` or else it
is set to ``LOW``.

Digital Read
------------

``digital_read`` is a function which enables PRU to read logic level at
specified input pin. It is a function with return type ``boolean`` and
it's parameter is a ``integer`` whose value must be the pin number to be
read or PRU R31 register bit.

.. _io-syntax-1:

Syntax
~~~~~~

``digital_read(pin_number);``

.. _parameters-1:

Parameters
^^^^^^^^^^

-  ``pin_number`` is an integer. It must be a header pin name which
   supports input, or PRU R31 Register bit.

.. _return-type-1:

Return Type
^^^^^^^^^^^

-  ``boolean`` - returns the logic level of the pin number passed to it.
   It returns ``true`` for HIGH and ``false`` for LOW.

.. _example-1:

Example
~~~~~~~

.. code:: python

   if digital_read(P1_20) {
       digital_write(P1_29, false);
   }
   else {
       digital_write(P1_29, true);
   }

Logic level of pin ``P1_20`` is read. If it is HIGH, then pin ``P1_29``
is set to ``LOW``, or else it is set to ``HIGH``.

Delay
-----

``delay`` is a function which makes PRU wait for specified milliseconds.
When this is called PRU does absolutely nothing, it just sits there
waiting.

.. _io-syntax-2:

Syntax
~~~~~~

``delay(time_in_ms);``

.. _parameters-2:

Parameters
^^^^^^^^^^

-  ``time_in_ms`` is an integer. It is the amount of time PRU should
   wait in milliseconds. (1000 milliseconds = 1 second).

.. _return-type-2:

Return Type
^^^^^^^^^^^

-  ``void`` - returns nothing.

.. _example-2:

Example
~~~~~~~

.. code:: python

   digital_write(P1_29, true);
   delay(2000);
   digital_write(P1_29, false);

Logic level of pin ``P1_29`` is set to ``HIGH``, PRU waits for *2000 ms*
= *2 seconds*, and then sets the logic level of pin ``P1_29`` to
``LOW``.

Start counter
-------------

``start_counter`` is a function which starts PRU's internal counter. It
counts number of CPU cycles. So it can be used to count time elapsed, as
it is known that each cycle takes 5 nanoseconds.

.. _io-syntax-3:

Syntax
~~~~~~

``start_counter()``

Parameters
^^^^^^^^^^

-  n/a

.. _return-type-3:

Return Type
^^^^^^^^^^^

-  ``void`` - returns nothing.

.. _example-3:

Example
~~~~~~~

.. code:: python

   start_counter();

Stop counter
------------

``stop_counter`` is a function which stops PRU's internal counter.

.. _io-syntax-4:

Syntax
~~~~~~

``stop_counter()``

.. _paramters-1:

Parameters
^^^^^^^^^^

-  n/a

.. _return-type-4:

Return Type
^^^^^^^^^^^

-  ``void`` - returns nothing.

.. _example-4:

Example
~~~~~~~

.. code:: python

   stop_counter();

Read counter
------------

``read_counter`` is a function which reads PRU's internal counter and
returns the value. It counts number of CPU cycles. So it can be used to
count time elapsed, as it is known that each cycle takes 5 nanoseconds.

.. _io-syntax-5:

Syntax
~~~~~~

``read_counter()``

.. _parameters-3:

Parameters
^^^^^^^^^^

-  n/a

.. _return-type-5:

Return Type
^^^^^^^^^^^

-  ``integer`` - returns the number of cycles elapsed since calling
   ``start_counter``.

.. _example-5:

Example
~~~~~~~

.. code:: python

   start_counter();

   while : read_counter < 200000000 {
       digital_write(P1_29, true);
   }

   digital_write(P1_29, false);
   stop_counter();

while the value of hardware counter is less than 200000000, it will set
logic level of pin ``P1_29`` to ``HIGH``, after that it will set it to
``LOW``. Here, 200000000 cpu cycles means 1 second of time, as CPU clock
is 200 MHz. So, LED will turn on for 1 second, and turn off after.

Init message channel
--------------------

``init_message_channel`` is a function which is used to initialise
communication channel between PRU and the ARM core. It is sets up
necessary structures to use RPMSG to communicate, it expects a init
message from the ARM core to initialise. It is a necessary to call this
function before using any of the message functions.

.. _io-syntax-6:

Syntax
~~~~~~

``init_message_channel()``

.. _parameters-4:

Parameters
^^^^^^^^^^

-  n/a

.. _return-type-6:

Return Type
^^^^^^^^^^^

-  ``void`` - returns nothing

.. _example-6:

Example
~~~~~~~

.. code:: python

   init_message_channel();

Receive message
---------------

``receive_message`` is a function which is used to receive messages from
ARM to the PRU, messages can only be ``integers``, as only they are
supported as of now. It uses RPMSG channel setup by
``init_message_channel`` to receive messages from ARM core.

.. _io-syntax-7:

Syntax
~~~~~~

``receive_message()``

.. _parameters-5:

Parameters
^^^^^^^^^^

-  n/a

.. _return-type-7:

Return Type
^^^^^^^^^^^

-  ``integer`` - returns integer data received from PRU

.. _example-7:

Example
~~~~~~~

.. code:: c

   init_message_channel();

   int temp := receive_message();

   if : temp >= 0 {
       digital_write(P1_29, true);
   }
   else {
       digital_write(P1_29, false);
   }

Send message
------------

There are six functions which are used to send messages to ARM core from
PRU, messages can be ``integers``, ``characters``, ``bools``,
``integer arrays``, ``character arrays``, and ``boolean arrays``. It
uses RPMSG channel setup by ``init_message_channel`` to send messages
from PRU to the ARM core.

For sending arrays, arrays are automatically converted to a string, for
example, [1, 2, 3, 4] would become “1 2 3 4”.

.. _io-syntax-8:

Syntax
~~~~~~

-  ``send_int(expression)``

-  ``send_char(expression)``

-  ``send_bool(expression)``

-  ``send_ints(identifier)``

-  ``send_chars(identifier)``

-  ``send_bools(identifier)``

-  ``send_message`` is an alias for ``send_int`` to preserve backwards
   compatibility.

.. _parameters-6:

Parameters
^^^^^^^^^^

-  For ``send_int`` and ``send_char``, ``expression`` would be an
   arithmetic expression.
-  For ``send_bool``, ``expression`` would be a boolean expression
-  For ``send_ints``, ``identifier`` should be an identifier for an
   integer array.
-  For ``send_chars``, ``identifier`` should be an identifier for a
   character array.
-  For ``send_bools``, ``identifier`` should be an identifier for a
   boolean array.

.. _example-8:

Example
~~~~~~~

.. code:: c

   init_message_channel();

   if : digital_read(P1_29) {
       send_bool(true);
   }
   else {
       send_int(0);
   }
