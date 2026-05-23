.. _rst-cheat-sheet:

ReStructuredText Cheat Sheet
############################

`BeagleBoard.org docs site <https://docs.beagleboard.org>`_ uses ReStructuredText (rst) which is a 
file format [#]_ for textual data used primarily in the Python programming language community 
for technical documentation. It is part of the Docutils project of the Python Doc-SIG, aimed at 
creating a set of tools for Python similar to Javadoc for Java or Plain Old Documentation for 
Perl. If you are new with rst you may go through this rst cheat sheet [#]_ [#]_ [#]_ chapter 
to gain enough skills to edit and update any page on the BeagleBoard.org docs site. some things 
you should keep in mind while working with rst,

1. like Python, RST syntax is sensitive to indentation !
2. RST requires blank lines between paragraphs

.. tip:: 

    Why not use Markdown for documentation? because reST stands out against Markdown as,
    
    1. It's more fully-featured.
    2. It's much more standardized and uniform.
    3. It has built-in support for extensions.

    For more detailed comparison you can checkout `this article on 
    reStructuredText vs. Markdown for technical documentation 
    <https://eli.thegreenplace.net/2017/restructuredtext-vs-markdown-for-technical-documentation/>`_ 

.. todo::

   There are several type of entries that should be added to the cheat sheet to help provide
   some consistency and avoid needing to refer to outside documentation.

   1. `todo` entries and general admonitions like `note` and `important`
   2. `literalinclude` usage
   3. `tab-set` entries
   4. `toctree` entires and policy (depth, etc.)
   5. Using `Separated Links`_

Text formatting
****************

With asterisk you can format the text as italic & bold,

1. Single asterisk (``*``) like ``*emphasis*`` gives you *italic text*
2. Double asterisk (``**``) like ``**strong emphasis**`` gives you **bold text**

With backquote character (`) you can format the text as link & inline literal.

1. See `Links and cross referencing`_ section on how single backquote can be used to create a link like `this <www.beagleboard.org>`_.
2. With double back quotes before and after text you can easily create ``inline lierals``.

.. note::
    backquote can be found below escape key on most keyboards.


Headings
*********

For each document we divide sections with headings and in ReStructuredText we can use 
matching overline and underline to indicate a heading. 

1. Document heading (H1) use ``#``.
2. First heading (H2) use ``*``.
3. Second heading (H3) use ``=``.
4. Third heading (H4) use ``-``.
5. Fourth heading (H5) use ``~``.

.. note::
    You can include only one (H1) ``#`` in a single documentation page.

Make sure the length of your heading symbol is at least (or 
more) the at least of the heading text, for example:


.. callout::

    .. code-block:: ReStructuredText

        incorrect H1
        ##### <1>

        correct H1
        ############ <2>
    
    .. annotations::

        <1> Length of heading symbol ``#`` is smaller than the content above.

        <2> Shows the correct way of setting the document title (H1) with ``#``.


Code
*****

For adding a code snippet you can use tab indentation to start. For more refined code snippet display
we have the ``code-block`` and ``literalinclude`` directives as shown below.


Indentation
============

This the simplest way of adding code snippet in ReStructuredText.

Example
-------

.. callout::

    .. code-block:: ReStructuredText

        This is python code:: <1>
            <2>
            import numpy as np <3>
            import math
    
    .. annotations::

        <1> Provide title of your code snippet and add ``::`` after the text.

        <2> Empty line after the title is required for this to work.

        <3> Start adding your code.


Output
------

This is python code::

    import numpy as np 
    import math

Code block
===========

Simple indentation only supports python program highlighting but, with code block you can 
specify which language is your code written in. ``code-block`` also provides better readability 
and line numbers support you can useas shown below.

Example
-------

.. callout::

    .. code-block:: ReStructuredText

        .. code-block:: python <1>
            :linenos: <2>

            import numpy as np <3>
            import math


    .. annotations::

        <1> Start with adding ``.. code-block::`` and then add language of code like python, bash, javascript, etc.
        
        <2> Optionally, you can enable line numbers for your code.

        <3> Start adding your code.

Output
------

.. code-block:: python
    :linenos: 

    import numpy as np
    import math


Literal include
================

To include the entire code or a code snippet from a program file you can use this directive.

Example
-------

.. callout::

    .. code-block:: ReStructuredText

        .. literalinclude:: filename.cpp <1>
            :caption: Example C++ file <2>
            :linenos: <3>
            :language: C++ <4>
            :lines: 2, 4-7 <5>
            :lineno-start: 113 <6>

    .. annotations::

        <1> Provide the code file destination.

        <2> Provide caption for the code.
        
        <3> Enable line numbers.

        <4> Set programming language.

        <5> Cherry pick some lines from a big program file.

        <6> Instead of starting line number from 1 start it with some other number. It's useful when you use :lines:, :start-after:, and :end-before:.

.. _rst-annotations:

Annotations
===========

We have a plug-in installed that enables annotated code blocks. Below is an example.

Example
-------

.. code-block:: ReStructuredText

    .. callout:: <1>

        .. code-block:: python <2>

            import numpy as np # <﻿1> <3>
            import math # <﻿2>

        .. annotations:: <4>

            <﻿1> Comment #1 <5>

            <﻿2> Comment #2

    .. annotations::

        <1> Indent everything under a `callout`

        <2> Create a normal block for what you want to annotate

        <3> Add ``<number>`` everywhere you want to annotate. Put it under a comment block if you want the code to run when copied directly.

        <4> Create an `annotations` block to hold your callout comments

        <5> Create an entry, separating each with a blank line and prefixing them with ``<number>``

Output
------

.. callout::

    .. code-block:: python

        import numpy as np # <1>
        import math # <2>

    .. annotations::

        <1> Comment #1

        <2> Comment #2

.. important::

    In the example, I inserted the invisible UTF character U+FEFF after the opening ``<`` to avoid it being
    interpreted as a callout symbol. Be sure to remove that character if you attempt to copy-and-paste the
    example.


Links and cross referencing
****************************

External links
==============

For a simple link (url) to a site the format is

.. code-block:: rst

    `<www.beagleboard.org>`_

this will be rendered as `<www.beagleboard.org>`_. 

You can also include a label to the link as shown below.

.. code-block:: rst

    `BeagleBoard.org <www.beagleboard.org>`_

this will be rendered as `BeagleBoard.org <www.beagleboard.org>`_. 

Cross referencing
==================

Cross referencing involves two components, references and targets.

1. **references** are pointers in your documentation to other parts of your documentation.
2. **targets** are where the references can point to.

When you manually create a target which can be referenced from other pages it's called 
explicit target. When you create a section (heading), a footnote, or a citation then 
Sphinx will create a target with the title as the name which is called implicit target 
which you can use within that page/document.

Implicit target
================

These are basically the headings inside the rst page which can 
be used as a link to that section within document. Taking the tile (name) 
of section ``External links`` as target we can reference it with syntax below: 

.. note:: 
        This can only be used within the document.

.. code-block:: rst

    `External links`_

Then the reference will be rendered as: `External links`_

Explicit target
================

These are special links you can assign to a specific part of the document and reference anywhere 
in the project unlike **implicit links which can be used only within the document they are defined**. 
On top of each page in docs you'll see some text like ``.. _rst-cheat-sheet:`` is used to create a
label for this chapter. These are called the explicit links amd you can reference these using ``ref:``.

.. note:: 
    This can be used inside or outside of the document and the rendered 
    link will take you directly to that specific section.

.. code-block:: rst

    :ref:`rst-cheat-sheet`

Then the reference will be rendered as: :ref:`rst-cheat-sheet`.

YouTube Videos
==============

This site uses sphinxcontrib-youtube to embed YouTube videos. The syntax is as follows:

.. callout::

    .. code-block:: ReStructuredText

        .. youtube:: <YouTube_video_ID> # <1>
            :width: 100% # <2>
            :align: center # <3>
    
    .. annotations::

        <1> Here you have to replace the <YouTube_video_ID> with your actual YouTube ID.

        <2> Enter width of the YouTube video player

        <3> Enter alignment of YouTube video player

When rendered, it looks like :ref:`youtube-example`.

.. _youtube-example:

YouTube video example 
-----------------------

.. youtube:: 7cm1AAnaawk
    :width: 100%
    :align: center

More
****

.. rubric:: footnotes

.. [#] `reStructuredText wiki page <https://en.wikipedia.org/wiki/ReStructuredText>`_

.. [#] `Sphinx and RST syntax guide (0.9.3) <https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html#internal-and-external-links>`_

.. [#] `Quick reStructuredText (sourceforge) <https://docutils.sourceforge.io/docs/user/rst/quickref.html#hyperlink-targets>`_

.. [#] `A two-page cheatsheet for restructured text <https://github.com/ralsina/rst-cheatsheet>`_

.. _Separated Links:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#external-links
