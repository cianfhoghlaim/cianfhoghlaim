.. _doc-builder:

Building the Documentation
##########################

We chose `Sphinx`_ as our tool for documenting BeagleBoard.org projects due to its popular use
in `Linux`_ and `Zephyr`_, two open source projects we respect a lot. This page is intended to
document specific aspects of the process of turning the `Docs Git Repo`_ into the `Docs Page`_.
This should help newcomers figure it out and those of us working on it a lot to simply remember
what we did.

Invoking Sphinx
***************

We rely primarily on invoking `Sphinx`_ from the `OpenBeagle CI`_.

.. literalinclude:: ../../.gitlab-ci.yml
    :language: YAML
    :caption: .gitlab-ci.yml
    :linenos:

.. _Sphinx:
   https://www.sphinx-doc.org/en/master/

.. _Linux:
   :ref:`Linux <intro-linux>`

.. _Zephyr:
   :ref:`Zephyr <intro-zephyr>`

.. _Docs Git Repo:
   https://openbeagle.org/docs/docs.beagleboard.io

.. _Docs Page:
   https://docs.beagleboard.org

.. _OpenBeagle CI:
   :ref:`OpenBeagle CI <intro-openbeagle-ci>`
